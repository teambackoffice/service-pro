import frappe
from frappe import _

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

def validate_margin_rate_with_rate(doc, method):
	"""Validate that rate field is not lower than custom_margin_rate for each item"""
	if not doc.items:
		return
    
	if frappe.session.user == "Administrator":
		return

	user_roles = frappe.get_roles(frappe.session.user)
	if "Margin Rate Approver" in user_roles:
		return
 
	
	validation_errors = []
	
	for idx, item in enumerate(doc.items):
		if hasattr(item, 'custom_margin_rate') and item.custom_margin_rate and item.rate:
			# Convert to float for comparison
			margin_rate = float(item.custom_margin_rate)
			item_rate = float(item.rate)
			
			# Check if item rate is lower than margin rate
			# Allow submission when rate >= margin_rate
			if item_rate < margin_rate:
				validation_errors.append({
					'row': idx + 1,
					'item_code': item.item_code,
					'item_name': item.item_name or item.item_code,
					'margin_rate': margin_rate,
					'item_rate': item_rate
				})
	
	if validation_errors:
		error_message = "Rate cannot be lower than Margin Rate for the following items:\n\n"
		
		for error in validation_errors:
			error_message += f"Row {error['row']}: ({error['item_code']})\n"
			error_message += f"  • Margin Rate: {error['margin_rate']:.2f}\n"
			error_message += f"  • Item Rate: {error['item_rate']:.2f}\n"
			error_message += f"  • Please increase Item Rate to at least {error['margin_rate']:.2f}\n\n"
		
		frappe.throw(_(error_message), title=_("Rate Below Margin Rate"))

def set_margin_rate_for_document_creator(doc):
	"""Set custom_margin_rate for new documents or update for document creator when their percentage changes"""
	if not doc.company:
		return
		
	current_user = frappe.session.user
	
	if doc.is_new() or doc.owner == current_user:
		user_margin_percentage = get_user_margin_percentage(current_user, doc.company)
		
		if user_margin_percentage is None:
			frappe.logger().info(f"No margin percentage found for user {current_user} in company {doc.company}")
			return
		
		should_update = False
		
		if doc.is_new():
			should_update = True
			frappe.logger().info(f"Setting margin rate {user_margin_percentage} for new document by {current_user}")
		elif doc.owner == current_user and doc.custom_margin_rate != user_margin_percentage:
			should_update = True
			frappe.logger().info(f"Updating margin rate from {doc.custom_margin_rate} to {user_margin_percentage} for document creator {current_user}")
		
		if should_update:
			doc.custom_margin_rate = user_margin_percentage
			
			for item in doc.items:
				if item.item_code and item.warehouse:
					calculate_item_margin_rate(doc, item)

def set_margin_rate_on_load(doc, method):
	"""Set margin rate based on user configuration only for document creator or new documents"""
	set_margin_rate_for_document_creator(doc)

@frappe.whitelist()
def on_submit_si(doc, method):
	if doc.owner == frappe.session.user:
		set_margin_rate_for_document_creator(doc)
	
	# Validate margin rate matches item rate before submission
	validate_margin_rate_with_rate(doc, method)
	
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

def before_save_si(doc, method):
	"""Set margin rate only for document creator or new documents"""
	set_margin_rate_for_document_creator(doc)

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

def validate_and_calculate_rates(doc, method):
    """Validate and calculate rates based on margin and valuation rate"""
    if doc.custom_margin_rate:
        for item in doc.items:
            if item.item_code and item.warehouse:
                calculate_item_margin_rate(doc, item)


def calculate_item_margin_rate(doc, item):
    """Calculate item margin rate using margin % and valuation rate"""
    try:
        cost_price = frappe.db.get_value("Bin", {
            "item_code": item.item_code,
            "warehouse": item.warehouse
        }, "valuation_rate")

        if not cost_price:
            return  # Skip if no cost price available

        margin_percentage = doc.custom_margin_rate
        margin_decimal = margin_percentage / 100

        if margin_decimal >= 1:
            frappe.throw(f"Margin percentage cannot be 100% or more for item {item.item_code}")

        selling_price = cost_price / (1 - margin_decimal)

        # Set calculated margin price to custom_margin_rate field in child table
        if hasattr(item, 'custom_margin_rate'):
            item.custom_margin_rate = selling_price
        else:
            frappe.logger().warning(f"'custom_margin_rate' field missing in Sales Invoice Item for {item.item_code}")

        frappe.logger().info(f"[Margin Calculation] Item: {item.item_code}, Cost: {cost_price}, "
                             f"Margin: {margin_percentage}%, Rate: {selling_price}")

    except Exception as e:
        frappe.logger().error(f"[Error] Margin calc failed for {item.item_code}: {str(e)}")


def get_user_margin_percentage(user, company):
    """Fetch user-specific margin percentage from Production Settings"""
    try:
        production_settings = frappe.get_doc("Production Settings", company)

        if hasattr(production_settings, 'default_sales_margin_percentage'):
            user_margin = next((row.percentage for row in production_settings.default_sales_margin_percentage
                                if row.user == user), None)
            return user_margin
    except Exception as e:
        frappe.logger().error(f"[Error] Fetching margin for user {user} in {company}: {str(e)}")
    return None


@frappe.whitelist()
def get_user_margin_rate():
    """Return current user's configured margin rate"""
    user = frappe.session.user
    company = frappe.defaults.get_user_default("Company")

    if not company:
        companies = frappe.get_all("Company", filters={"disabled": 0}, fields=["name"], limit=1)
        if companies:
            company = companies[0].name

    return get_user_margin_percentage(user, company)


@frappe.whitelist()
def calculate_selling_price(cost_price, margin_percentage):
    """Calculate selling price given a cost and margin"""
    try:
        cost_price = float(cost_price)
        margin_percentage = float(margin_percentage)

        if cost_price <= 0:
            frappe.throw(_("Cost price must be greater than 0"))

        if not (0 < margin_percentage < 100):
            frappe.throw(_("Margin percentage must be between 0 and 100"))

        margin_decimal = margin_percentage / 100
        selling_price = cost_price / (1 - margin_decimal)

        return {
            "cost_price": cost_price,
            "margin_percentage": margin_percentage,
            "selling_price": selling_price,
            "margin_amount": selling_price - cost_price
        }

    except Exception as e:
        frappe.throw(_("Error calculating selling price: {0}").format(str(e)))


def calculate_item_rate_with_margin(doc, item):
    """[REFERENCE] Compute and update rate field instead of custom_margin_rate"""
    try:
        cost_price = frappe.db.get_value("Bin", {
            "item_code": item.item_code,
            "warehouse": item.warehouse
        }, "valuation_rate")

        if not cost_price:
            return

        margin_percentage = doc.custom_margin_rate
        margin_decimal = margin_percentage / 100

        if margin_decimal >= 1:
            frappe.throw(f"Margin percentage cannot be 100% or more for item {item.item_code}")

        selling_price = cost_price / (1 - margin_decimal)
        item.rate = selling_price  # Reference update

        frappe.logger().info(f"[Ref Margin] Item: {item.item_code}, Cost: {cost_price}, "
                             f"Margin: {margin_percentage}%, Rate: {selling_price}")

    except Exception as e:
        frappe.logger().error(f"[Ref Error] Margin rate set failed for {item.item_code}: {str(e)}")