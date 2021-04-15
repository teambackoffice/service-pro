import frappe

def generate_jv(doc):
	if doc.paid:
		doc_jv = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": doc.posting_date,
			"sales_invoice": doc.name,

			"accounts": jv_accounts_paid(doc),
		}

		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()
		frappe.db.sql(""" UPDATE `tabSales Invoice` SET journal_entry=%s WHERE name=%s""", (jv.name, doc.name))
		frappe.db.commit()

	elif doc.unpaid:
		doc_jv = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": doc.posting_date,
			"sales_invoice": doc.name,
			"accounts": jv_accounts_unpaid(doc),
		}

		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()
		doc.journal_entry = jv.name
		frappe.db.sql(""" UPDATE `tabSales Invoice` SET journal_entry=%s WHERE name=%s""", (jv.name, doc.name))
		frappe.db.commit()
def jv_accounts_unpaid(doc):
	accounts = []
	accounts.append({
		'account': doc.expense_account,
		'debit_in_account_currency': doc.incentive,
		'credit_in_account_currency': 0,
		'cost_center': doc.expense_cost_center,
	})
	accounts.append({
		'account': doc.liabilities_account,
		'debit_in_account_currency': 0,
		'credit_in_account_currency': doc.incentive
	})
	return accounts

def jv_accounts_paid(doc):
	accounts = []
	accounts.append({
		'account': doc.expense_account,
		'debit_in_account_currency': doc.incentive,
		'credit_in_account_currency': 0,
		'cost_center': doc.expense_cost_center,
	})
	if doc.cash:
		mop_cash = frappe.db.sql(""" SELECT * FROM `tabMode of Payment Account` WHERE parent=%s """, (doc.showroom_cash), as_dict=1)
		if len(mop_cash) > 0:
			accounts.append({
				'account': mop_cash[0].default_account,
				'debit_in_account_currency': 0,
				'credit_in_account_currency': doc.incentive
			})
	return accounts
@frappe.whitelist()
def on_submit_si(doc, method):
	if len(doc.sales_team) > 0 and not doc.paid and not doc.unpaid:
		frappe.throw("Please select Paid or Unpaid for Sales Person")

	generate_jv(doc)
	for prod in doc.production:
		production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
		if len(production) > 0:
			if doc.update_stock and get_dn_si_qty("", production[0].qty, prod.reference) > 0 :
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("Partially Delivered", prod.reference))
				frappe.db.commit()

			elif get_dn_si_qty("", production[0].qty, prod.reference) == 0 and get_lengths(prod.reference)[0] == get_lengths(prod.reference)[1] :

				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Completed", prod.reference))
				frappe.db.commit()
				get_service_records(prod.reference)

			elif get_dn_qty(prod.reference) >= 0 and \
                    ((get_dn_si_qty("", production[0].qty, prod.reference) >= 0 and get_lengths(prod.reference)[0] !=
                             get_lengths(prod.reference)[1])):
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Deliver", prod.reference))
				frappe.db.commit()

			elif get_dn_si_qty("", production[0].qty, prod.reference) > 0:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("Partially Delivered", prod.reference))
				frappe.db.commit()

def get_service_records(reference):
	estimation_ = ""
	estimation = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name= %s""", reference, as_dict=1)
	if len(estimation) > 0:
		estimation_ = estimation[0].estimation
		frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s""",
					  ("Completed", estimation_))

	inspections = frappe.db.sql(""" SELECT * FROM `tabInspection Table` WHERE parent=%s """, estimation_, as_dict=1)
	for i in inspections:
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s""",
					  ("Completed", i.inspection))

	srn = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE name=%s """, estimation_, as_dict=1)
	if len(srn) > 0:
		srn_ = srn[0].receipt_note
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s""",
					 ("Completed", srn_))
	frappe.db.commit()


def get_service_records_cancel(reference):
	estimation_ = ""
	estimation = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name= %s""", reference, as_dict=1)
	if len(estimation) > 0:
		estimation_ = estimation[0].estimation
		frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s""",
					  ("To Production", estimation_))

	inspections = frappe.db.sql(""" SELECT * FROM `tabInspection Table` WHERE parent=%s """, estimation_, as_dict=1)
	for i in inspections:
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s""",
					  ("To Production", i.inspection))

	srn = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE name=%s """, estimation_, as_dict=1)
	if len(srn) > 0:
		srn_ = srn[0].receipt_note
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s""",
					  ("To Production", srn_))
	frappe.db.commit()

@frappe.whitelist()
def on_cancel_si(doc, method):
	for prod in doc.production:
		production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
		if len(production) > 0:
			if doc.update_stock:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Deliver and Bill", prod.reference))
				frappe.db.commit()
				get_service_records(prod.reference)

			elif get_lengths(prod.reference)[0] == 0 and get_lengths(prod.reference)[1] == 0:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("To Deliver and Bill", prod.reference))
				frappe.db.commit()
				get_service_records(prod.reference)

			elif get_dn_qty(prod.reference) >= 0 and \
					((get_dn_si_qty("", production[0].qty, prod.reference) >= 0 and get_lengths(prod.reference)[0] !=
						get_lengths(prod.reference)[1])):
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Bill", prod.reference))
				frappe.db.commit()

			elif get_dn_si_qty("", production[0].qty, prod.reference) > 0:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("Partially Delivered", prod.reference))
				frappe.db.commit()
	if doc.journal_entry:
		frappe.db.sql(""" UPDATE `tabJournal Entry` SET sales_invoice='' WHERE name=%s """, doc.journal_entry)
		frappe.db.commit()

def get_lengths(name):
	si_query = """ 
     			SELECT SIP.qty as qty, SI.status FROM `tabSales Invoice` AS SI 
     			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
     			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1 and SI.status!='Cancelled' and SI.update_stock = 0
     			"""
	si = frappe.db.sql(si_query, (name, "Sales Invoice"), as_dict=1)
	dn_query = """ 
    	 			SELECT SIP.qty as qty, DN.status FROM `tabDelivery Note` AS DN 
    	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
    	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1 and DN.status!='Cancelled'
    	 			"""
	dn = frappe.db.sql(dn_query, (name, "Delivery Note"), as_dict=1)

	return len(dn), len(si)
def get_dn_si_qty(item_code, qty, name):
	si_query = """ 
 			SELECT SIP.qty as qty, SI.status FROM `tabSales Invoice` AS SI 
 			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
 			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1 and SI.status!='Cancelled'
 			"""
	si = frappe.db.sql(si_query,(name,"Sales Invoice"), as_dict=1)
	dn_query = """ 
	 			SELECT SIP.qty as qty, DN.status FROM `tabDelivery Note` AS DN 
	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1 and DN.status!='Cancelled'
	 			"""
	dn = frappe.db.sql(dn_query,(name, "Delivery Note"), as_dict=1)

	total_qty = 0

	if len(si) > len(dn):
		for i in si:
			total_qty += i.qty

	elif len(dn) > len(si):
		for d in dn:
			total_qty += d.qty
	elif len(dn) == len(si):
		for d in dn:
			total_qty += d.qty
	return float(qty) - float(total_qty)



def get_dn_qty(name):

	dn_query = """ 
	 			SELECT SIP.qty as qty, DN.status FROM `tabDelivery Note` AS DN 
	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1 and DN.status!='Cancelled'
	 			"""
	dn = frappe.db.sql(dn_query, (name, "Delivery Note"), as_dict=1)

	total_qty = 0

	if len(dn) > 0:
		for d in dn:
			total_qty += d.qty

	return float(total_qty)