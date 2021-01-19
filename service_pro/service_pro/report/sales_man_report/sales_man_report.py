# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("customer"):
		conditions += " and customer='{0}' ".format(filters.get("customer"))

	if len(filters.get("status")) > 1:
		status_array = []
		for i in filters.get("status"):
			status_array.append(i)
		print(status_array)
		conditions += " and status in {0} ".format(tuple(status_array))
	elif len(filters.get("status")) == 1:
		conditions += " and status='{0}' ".format(filters.get("status")[0])

	elif not filters.get("status"):
		columns.append({"label": "Status ", "fieldname": "status", "fieldtype": "Data", "options": "Sales Invoice", "width": "80"})

	if filters.get("sales_man"):
		conditions += " and sales_man='{0}' ".format(filters.get("sales_man"))

	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Link", "options": "Production", "width": "100"},
		{"label": "Sales Invoice", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": "130"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "280"},
		{"label": "Sales Man Name", "fieldname": "sales_man_name", "fieldtype": "Data", "width": "200"},
		{"label": "Net Total", "fieldname": "total", "fieldtype": "Currency", "width": "100"},
		{"label": "VAT", "fieldname": "total_taxes_and_charges", "fieldtype": "Currency", "width": "100"},
		{"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": "100"},
		{"label": "Agent Comm.", "fieldname": "incentive", "fieldtype": "Currency", "width": "110"},
		{"label": "Net Amount", "fieldname": "net_amount", "fieldtype": "Currency", "width": "100"},
		{"label": "Status ", "fieldname": "status", "fieldtype": "Data", "options": "Sales Invoice", "width": "80"},
	]
	query = """ SELECT * FROM `tabSales Invoice` WHERE docstatus=1 {0}""".format(conditions)
	print(query)
	data = frappe.db.sql(query, as_dict=1)
	for i in data:
		i['net_amount'] = i.total - i.incentive if i.incentive > 0 else i.total

	return columns, data
