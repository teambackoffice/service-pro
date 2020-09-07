# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), []

	condition = ""
	query_ = ""
	if filters.get("paid_disabled"):
		condition += " and "
		condition += " SI.status!='{0}' ".format("Paid")
	if len(filters.get("mop")) > 1:
		mop_array = []
		for i in filters.get("mop"):
			mop_array.append(i)
		query_ += " INNER JOIN `tabSales Invoice Payment` AS SIP ON SIP.parent = SI.name and SIP.mode_of_payment in {0} and SI.paid = 1 and SI.showroom_cash in {1}".format(tuple(mop_array),tuple(mop_array))
	elif len(filters.get("mop")) == 1:
		query_ += " INNER JOIN `tabSales Invoice Payment` AS SIP ON SIP.parent = SI.name and SIP.mode_of_payment = '{0}' and SI.paid = 1 and SI.showroom_cash = '{1}'".format(filters.get("mop")[0],filters.get("mop")[0])

	if filters.get("customer"):
		condition += " and "
		condition += " SI.customer='{0}' ".format(filters.get("customer"))

	if filters.get("invoice_number"):
		condition += " and "
		condition += " SI.name='{0}' ".format(filters.get("invoice_number"))

	if filters.get("to_date") and filters.get("from_date"):
		condition += " and "
		condition += "SI.posting_date BETWEEN '{0}' and '{1}'".format(filters.get("to_date"),filters.get("from_date"))

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
 					(SELECT incentives FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as insentive,
 					SI.status as status
				FROM `tabSales Invoice` AS SI {0} WHERE SI.docstatus = 1 {1}""".format(query_,condition)

	datas = frappe.db.sql(query,as_dict=1)

	new_data = []
	for i in datas:
		print(i.mop)
		i['advance'] = 0
		i['net_amount'] = i.grand_total
		if i.unpaid:
			i['incentive_unpaid'] = i.incentive
		new_data.append(i)
		if i.paid:
			new_data.append({
				"date": i.date,
				"si_no": i.name,
				"customer_name": i.customer_name,
				"sales_man_agent": i.sales_man_agent,
				"mop": i.showroom_cash if i.cash else "",
				"incentive_paid": 0 - i.incentive,
				"net_amount": 0 - i.incentive

			})
	jv_add(filters, new_data)
	pe_add(filters, new_data)
	return columns, new_data

def pe_add(filters, new_data):
	condition_pe = ""
	if filters.get("from_date") and filters.get("to_date"):
		condition_pe += " and PE.posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),
																			  filters.get("to_date"))

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
	print(payment_entry_query)
	pe = frappe.db.sql(payment_entry_query, as_dict=1)
	for iii in pe:
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
    if filters.get("from_date") and filters.get("to_date"):
        condition_jv += " and JE.posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),
                                                                              filters.get("to_date"))

    if filters.get("customer"):
        condition_jv += " and party='{0}' ".format(filters.get("customer"))

    jv_query = """ 
    				SELECT JE.name, JE.posting_date, JEI.party, JEI.credit_in_account_currency FROM `tabJournal Entry`AS JE 
    				INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
    				WHERE JEI.is_advance = 'Yes'
    					and JEI.party_type = 'Customer'
    					and JE.docstatus=1 {0}""".format(condition_jv)

    jv = frappe.db.sql(jv_query, as_dict=1)
    for ii in jv:
        new_data.append({
            "date": ii.posting_date,
            "customer_name": ii.party,
            "si_no": ii.name,
            "advance": ii.credit_in_account_currency,
            "net_amount": ii.credit_in_account_currency,
        })
def check_jv_in_data(new_data, jv):
	for i in new_data:
		if i["si_no"] == jv[0].parent:
			return False
	return True

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