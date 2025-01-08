import frappe

def generate_jv(doc):
	if doc.paid:
		data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments Details` WHERE company=%s """, doc.company,
							 as_dict=1)

		doc_jv = {
			"doctype": "Sales Partner Payments",
			"sales_partner_name": doc.sales_partner,
			"company": doc.company,
			"incentive": doc.incentive,
			"balance_amount": doc.incentive,
			"posting_date": doc.posting_date,
			"status": "Paid",
			"sales_invoice_reference": doc.name,
			"invoice_net_amount": doc.total,
			"customer_id": doc.customer,
			"customer_name": doc.customer_name,
			"cost_center": doc.cost_center,
		}
		if len(data) == 0:
			frappe.throw("Please set Sales Partner Payments Details defaults in Production Settings")
		if len(data) > 0 and not data[0].payable_account:
			frappe.throw("Please set Payable Account in Sales Partner Payments Details defaults in Production Settings")

		if len(data) > 0 and not data[0].expense_accounts:
			frappe.throw("Please set Expense Account in Sales Partner Payments Details defaults in Production Settings")

		if not doc.showroom_cash and not data[0].showroom_cash:
			frappe.throw("Please set Showroom Cash in Production Settings")

		mop_cash = frappe.db.sql(""" SELECT * FROM `tabMode of Payment Account` WHERE parent=%s and company=%s""", (doc.showroom_cash or data[0].showroom_cash,doc.company),
								 as_dict=1)

		if len(mop_cash) > 0:
			doc_jv['payable_account'] = mop_cash[0].default_account
		else:
			frappe.throw("Please add account for company " + doc.company + " in Mode of Payment " + doc.showroom_cash or data[0].showroom_cash)
		doc_jv['expense_account'] = data[0].expense_accounts
		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()
		frappe.msgprint("Sales Partner Payments Created")
	elif doc.unpaid:
		data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments Details` WHERE company=%s """,doc.company, as_dict=1)

		doc_jv = {
			"doctype": "Sales Partner Payments",
			"company": doc.company,
			"sales_partner_name": doc.sales_partner,
			"incentive": doc.incentive,
			"balance_amount": doc.incentive,
			"posting_date": doc.posting_date,
			"status": "Unpaid",
			"sales_invoice_reference": doc.name,
			"invoice_net_amount": doc.total,
			"customer_id": doc.customer,
			"customer_name": doc.customer_name,
			"cost_center": doc.cost_center,
		}
		if len(data) == 0:
			frappe.throw("Please set Sales Partner Payments Details defaults in Production Settings")
		if len(data) > 0 and not data[0].payable_account:
			frappe.throw("Please set Payable Account in Sales Partner Payments Details defaults in Production Settings")

		if len(data) > 0 and not data[0].expense_accounts:
			frappe.throw("Please set Expense Account in Sales Partner Payments Details defaults in Production Settings")

		doc_jv['payable_account'] = data[0].payable_account
		doc_jv['expense_account'] = data[0].expense_accounts
		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()
		frappe.msgprint("Sales Partner Payments Created")
		# doc.journal_entry = jv.name
		# frappe.db.sql(""" UPDATE `tabSales Invoice` SET journal_entry=%s WHERE name=%s""", (jv.name, doc.name))
		# frappe.db.commit()
def jv_accounts_unpaid(doc):
	data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments` WHERE company=%s """, doc.company, as_dict=1)
	if len(data) == 0:
		frappe.throw("Please setup Sales Partner Payments for company " + doc.company)
	accounts = []
	accounts.append({
		'account': data[0].expense_accounts,
		'debit_in_account_currency': doc.incentive,
		'credit_in_account_currency': 0,
		'cost_center': doc.expense_cost_center,
	})
	accounts.append({
		'account':data[0].payable_account,
		'debit_in_account_currency': 0,
		'credit_in_account_currency': doc.incentive
	})
	return accounts

def jv_accounts_paid(doc):
	data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments` WHERE company=%s """, doc.company,as_dict=1)
	if len(data) == 0:
		frappe.throw("Please setup Sales Partner Payments for company " + doc.company)
	accounts = []
	accounts.append({
		'account': data[0].expense_accounts,
		'debit_in_account_currency': doc.incentive,
		'credit_in_account_currency': 0,
		'cost_center': doc.expense_cost_center,
	})
	if doc.cash:
		if not doc.showroom_cash and not data[0].showroom_cash:
			frappe.throw("Please set Showroom Cash in Production Settings")

		mop_cash = frappe.db.sql(""" SELECT * FROM `tabMode of Payment Account` WHERE parent=%s and company=%s """, (doc.showroom_cash or data[0].showroom_cash,doc.company), as_dict=1)
		if len(mop_cash) > 0:
			accounts.append({
				'account': mop_cash[0].default_account,
				'debit_in_account_currency': 0,
				'credit_in_account_currency': doc.incentive
			})
		else:
			frappe.throw("Please add account for company " + doc.company + " in Mode of Payment " + doc.showroom_cash or data[0].showroom_cash)
	else:
		accounts.append({
			'account': data[0].payable_account,
			'debit_in_account_currency': 0,
			'credit_in_account_currency': doc.incentive
		})
	return accounts
@frappe.whitelist()
def on_submit_si(doc, method):
	if doc.selling_price_list:
		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
			over_disc = frappe.db.exists("Sales Invoice Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
			if max_disc and over_disc:
				frappe.throw(" Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Sales Invoice Item", over_disc, ['item_code'])))

	if doc.sales_partner and not doc.paid and not doc.unpaid:
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


def validate_so(doc, method):

	if frappe.db.get_single_value("Production Settings", "enable_sales_order_validation"):
		if not doc.is_pos:
			for it in doc.get("items"):
				if not it.sales_order:
					frappe.throw("The Item {0}-{1} Does not have Sales Order".format(it.item_code,it.item_name))

def validate_permission(doc, method):
	if not doc.custom_ignore_permission_ and not doc.custom_production_id:
		frappe.throw("Sales Invoice is Required")

@frappe.whitelist()
def get_role():
	doc = frappe.db.get_value("Production Settings",None,"ignore_permission")
	return doc