# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), []

	condition = ""
	if filters.get("paid_disabled"):
		condition += " and "
		condition += " SI.status!='{0}' ".format("Paid")

	if filters.get("customer"):
		condition += " and "
		condition += " SI.customer='{0}' ".format(filters.get("customer"))

	if filters.get("invoice_number"):
		condition += " and "
		condition += " SI.name='{0}' ".format(filters.get("invoice_number"))

	if filters.get("to_date"):
		condition += " and "
		condition += "SI.posting_date = '{0}'".format(filters.get("to_date"))

	if filters.get("pos_profile"):
		condition += " and "

		condition += "SI.pos_profile='{0}' and SI.is_pos = 1".format(filters.get("pos_profile"))

	if filters.get("warehouse"):
		condition += " and "

		condition += "SI.set_warehouse='{0}'".format(filters.get("warehouse"))

	if len(filters.get("cost_center")) > 1:
		condition += " and "
		cost_center_array = []
		for i in filters.get("cost_center"):
			cost_center_array.append(i)

		condition += "SI.cost_center in {0}".format(tuple(cost_center_array))
	elif len(filters.get("cost_center")) == 1:
		condition += " and "

		condition += "SI.cost_center = '{0}'".format(filters.get("cost_center")[0])

	query = """ SELECT 
                    SI.name,
 					SI.posting_date as date,
 					SI.name as si_no,
 					SI.customer,
 					(SELECT customer_name FROM `tabCustomer` AS C WHERE C.name = SI.customer) as customer_name,
 					(SELECT sales_person FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as sales_man_agent,
					(SELECT mode_of_payment FROM `tabSales Invoice Payment` AS SIP WHERE SIP.parent = SI.name LIMIT 1) as mop,
					SI.total_taxes_and_charges as vat,
 					SI.total as total,
 					SI.paid,
 					SI.unpaid,
 					SI.incentive,
 					SI.showroom_card,
 					SI.showroom_cash,
 					SI.cash,
 					SI.card,
 					SI.discount_amount as discount,
 					SI.net_total as net_total,
 					SI.grand_total as grand_total,
 					SI.is_pos,
 					SI.journal_entry,
 					(SELECT incentives FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as insentive,
 					SI.status as status
				FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1 {0}""".format(condition)

	datas = frappe.db.sql(query,as_dict=1)

	new_data = []
	list_of_pe = []
	for i in datas:
		print(i.mop)
		i['advance'] = 0
		i['net_amount'] = i.grand_total if not get_pe(i.name, filters.get("to_date")) else 0

		if i.unpaid:
			i['incentive_unpaid'] = i.incentive

		if not filters.get("mop") or (filters.get("mop") and i.mop in filters.get("mop")):
			new_data.append(i)

		if (not filters.get("mop") or (i.paid and i.showroom_cash in filters.get("mop"))) and i.incentive > 0 and not i.journal_entry:
			new_data.append({
				"date": i.date,
				"si_no": i.name,
				"customer_name": i.customer_name,
				"sales_man_agent": i.sales_man_agent,
				"mop": i.showroom_cash if i.cash else "",
				"incentive_paid": 0 - i.incentive,
				"net_amount": 0 - i.incentive
			})
		# pe = get_pe(i.name, filters.get("to_date"))
		# if pe:
		# 	if (filters.get("mop") and pe[0].mode_of_payment in filters.get("mop")) or not filters.get("mop"):
		# 		new_data.append({
		# 			"date": pe[0].posting_date,
		# 			"customer_name": i.customer_name,
		# 			"si_no": pe[0].parent,
		# 			"mop": pe[0].mode_of_payment,
		# 			"payment_receive": pe[0].paid_amount,
		# 			"net_amount": pe[0].paid_amount,
		# 		})
		# 		list_of_pe.append(pe[0].name)

	pe_add(filters, new_data)
	jv_add(filters, new_data)
	jv_add_not_advance(filters, new_data)
	return columns, new_data
def get_pe(name, date):
	condition = ""
	if date:
		condition = "WHERE PE.posting_date = '{0}'".format(date)

	query = """ SELECT * FROM `tabPayment Entry` AS PE INNER JOIN `tabPayment Entry Reference` AS PER ON  PER.parent = PE.name and PER.reference_name='{0}' {1}""".format(name, condition)
	pe = frappe.db.sql(query, as_dict=1)
	if len(pe) > 0:
		return pe
	return None
def pe_add(filters, new_data):
	condition_pe = ""
	if filters.get("to_date"):
		condition_pe += " and PE.posting_date = '{0}'".format(filters.get("to_date"))

	if filters.get("customer"):
		condition_pe += " and PE.party='{0}' ".format(filters.get("customer"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		for i in filters.get("mop"):
			mop_array.append(i)
		condition_pe += " and PE.mode_of_payment in {0} ".format(tuple(mop_array))

	elif len(filters.get("mop")) == 1:
		condition_pe += " and PE.mode_of_payment = '{0}' ".format(filters.get("mop")[0])

	payment_entry_query = """
					SELECT * FROM `tabPayment Entry`AS PE 
					WHERE PE.docstatus= 1 {0}""".format(condition_pe)
	pe = frappe.db.sql(payment_entry_query, as_dict=1)
	for iii in pe:
		# if iii.name not in list_of_pe:
		new_data.append({
			"date": iii.posting_date,
			"customer_name": iii.party_name,
			"si_no": iii.name,
			"mop": iii.mode_of_payment,
			"payment_receive":iii.paid_amount,
			"net_amount":iii.paid_amount,
		})
def jv_add(filters, new_data):
	condition_jv = ""
	if filters.get("to_date"):
		condition_jv += " and JE.posting_date ='{0}' ".format(filters.get("to_date"))

	if filters.get("customer"):
		condition_jv += " and party='{0}' ".format(filters.get("customer"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		mop_name = "or JEI.account like "
		for i in filters.get("mop"):
			mop_array.append(i)

		if "Showroom Cash" in mop_array:
			mop_name += "'%Showroom Accrual - Cash%'"

		if "Showroom Card" in mop_array:
			if "Showroom Accrual - Cash" in mop_name:
				mop_name += " or JEI.account like '%Showroom Accrual - Card%'"
			else:
				mop_name += " JEI.account like '%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment in {0} {1})".format(tuple(mop_array), mop_name)

	elif len(filters.get("mop")) == 1:
		mop_name = "or JEI.account like "
		if filters.get("mop")[0] == "Showroom Cash":
			print("WHAAAAT")
			mop_name += "'%Showroom Accrual - Cash%'"

		if filters.get("mop")[0] == "Showroom Card":
			mop_name += "'%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment = '{0}' {1})".format(filters.get("mop")[0], mop_name)

	jv_query = """ 
					SELECT JE.name, JE.posting_date, JEI.party, JEI.debit_in_account_currency FROM `tabJournal Entry`AS JE 
					INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
					WHERE JEI.is_advance = 'Yes' and JEI.debit_in_account_currency > 0 and JE.docstatus=1 {0}""".format(condition_jv)
	print("======================================================")
	print(jv_query)
	jv = frappe.db.sql(jv_query, as_dict=1)
	for ii in jv:
		if not check_jv_in_data(new_data, ii.name):
			new_data.append({
				"date": ii.posting_date,
				"customer_name": ii.party,
				"si_no": ii.name,
				"advance": ii.debit_in_account_currency,
				"net_amount": ii.debit_in_account_currency,
			})

def jv_add_not_advance(filters, new_data):
	condition_jv = ""
	if filters.get("to_date"):
		condition_jv += " and JE.posting_date ='{0}' ".format(filters.get("to_date"))
    #
	# if filters.get("customer"):
	# 	condition_jv += " and party='{0}' ".format(filters.get("customer"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		mop_name = "or JEI.account like "
		for i in filters.get("mop"):
			mop_array.append(i)

		if "Showroom Cash" in mop_array:
			mop_name += "'%Showroom Accrual - Cash%'"

		if "Showroom Card" in mop_array:
			if "Showroom Accrual - Cash" in  mop_name:
				mop_name += " or JEI.account like '%Showroom Accrual - Card%'"
			else:
				mop_name += " JEI.account like '%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment in {0} {1})".format(tuple(mop_array), mop_name)


	elif len(filters.get("mop")) == 1:

		mop_name = "or JEI.account like "

		if filters.get("mop")[0] == "Showroom Cash":
			print("WHAAAAT")

			mop_name += "'%Showroom Accrual - Cash%'"

		if filters.get("mop")[0] == "Showroom Card":
			mop_name += "'%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment = '{0}' {1})".format(filters.get("mop")[0], mop_name)

	jv_query = """ 
					SELECT JE.name, JE.posting_date, JEI.party, JEI.credit_in_account_currency, JE.mode_of_payment FROM `tabJournal Entry`AS JE 
					INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
					WHERE JEI.is_advance = 'No' and JEI.credit_in_account_currency > 0
						and JE.docstatus=1 {0}""".format(condition_jv)

	jv = frappe.db.sql(jv_query, as_dict=1)
	for ii in jv:
		if not check_jv_in_data(new_data, ii.name):
			new_data.append({
				"date": ii.posting_date,
				"customer_name": ii.party,
				"si_no": ii.name,
				"incentive_paid": 0 - ii.credit_in_account_currency,
				"net_amount": 0 - ii.credit_in_account_currency,
				"mop": ii.mode_of_payment,
			})
def check_jv_in_data(new_data, jv):
	for i in new_data:
		if i["si_no"] == jv:
			return True
	return False

def get_columns():
	columns = [
		{"label": "Date", "fieldname": "date", "fieldtype": "Date","width": "100"},
		{"label": "SI No", "fieldname": "si_no", "fieldtype": "Link","options": "Sales Invoice","width": "150"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "150"},
		{"label": "Sales Man/Agent", "fieldname": "sales_man_agent", "fieldtype": "Data", "width": "150"},
		{"label": "MOP", "fieldname": "mop", "fieldtype": "Data", "width": "120"},
		{"label": "Payment Receive", "fieldname": "payment_receive", "fieldtype": "Data", "width": "120"},
		{"label": "Advance", "fieldname": "advance", "fieldtype": "Float", "precision": "2", "width": "100"},

		{"label": "Total", "fieldname": "total", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Discount", "fieldname": "discount", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Net Total", "fieldname": "net_total", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "VAT", "fieldname": "vat", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "Grand Total", "fieldname": "grand_total","fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Incentive Paid", "fieldname": "incentive_paid", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Incentive Unpaid", "fieldname": "incentive_unpaid", "fieldtype": "Float","precision": "2","width": "120"},
		{"label": "Net Amount", "fieldname": "net_amount", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data","width": "100"},
	]
	return columns