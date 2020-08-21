# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), []

	condition = ""
	query_ = ""
	if len(filters.get("mop")) > 1:
		mop_array = []
		for i in filters.get("mop"):
			mop_array.append(i)
		query_ += " INNER JOIN `tabSales Invoice Payment` AS SIP ON SIP.parent = SI.name and SIP.mode_of_payment in {0} ".format(tuple(mop_array))
	elif len(filters.get("mop")) == 1:
		query_ += " INNER JOIN `tabSales Invoice Payment` AS SIP ON SIP.parent = SI.name and SIP.mode_of_payment = '{0}' ".format(filters.get("mop")[0])

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
 					SI.posting_date as date,
 					SI.name as si_no,
 					(SELECT customer_name FROM `tabCustomer` AS C WHERE C.name = SI.customer) as customer_name,
 					(SELECT sales_person FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as sales_man_agent,
					(SELECT mode_of_payment FROM `tabSales Invoice Payment` AS SIP WHERE SIP.parent = SI.name LIMIT 1) as mop,
					SI.total_taxes_and_charges as vat,
 					(SELECT allocated_amount FROM `tabSales Invoice Advance` AS A WHERE A.parent = SI.name LIMIT 1) as advance,
 					SI.total as net_total,
 					SI.grand_total as grand_total,
 					(SELECT incentives FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as insentive,
 					SI.total - (SELECT incentives FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as net_amount,
 					SI.status as status
				FROM `tabSales Invoice` AS SI {0} WHERE SI.docstatus = 1 {1}""".format(query_,condition)
	print(query)
	data = frappe.db.sql(query,as_dict=1)


	return columns, data


def get_columns():
	columns = [
		{"label": "Date", "fieldname": "date", "fieldtype": "Date","width": "100"},
		{"label": "SI No", "fieldname": "si_no", "fieldtype": "Link","options": "Sales Invoice","width": "150"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "150"},
		{"label": "Sales Man/Agent", "fieldname": "sales_man_agent", "fieldtype": "Data", "width": "150"},
		{"label": "MOP", "fieldname": "mop", "fieldtype": "Data", "width": "100"},
		{"label": "VAT", "fieldname": "vat", "fieldtype": "Float","precision": "2", "width": "100"},
		{"label": "Advance", "fieldname": "advance", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Net Total", "fieldname": "net_total", "fieldtype": "Float","precision": "2","width": "100"},

		{"label": "Grand Total", "fieldname": "grand_total","fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Insentive", "fieldname": "insentive", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Net Amount", "fieldname": "net_amount", "fieldtype": "Float","precision": "2","width": "100"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data","width": "100"},
	]
	return columns