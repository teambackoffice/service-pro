# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = [
		{"label": "Series", "fieldname": "name", "fieldtype": "Link", "options": "Production", "width": "120"},
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date","width": "100"},
		{"label": "Delivery Date", "fieldname": "delivery_date", "fieldtype": "Data","width": "150"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "150"},
		{"label": "Finished Good", "fieldname": "item_name", "fieldtype": "Data", "width": "150"},
		{"label": "Qty", "fieldname": "qty", "fieldtype": "Data", "width": "120"},
		{"label": "Sales Man Name", "fieldname": "sales_man_name", "fieldtype": "Data", "width": "120"},

	]

	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("status"):
		conditions += " and status = '{0}'".format(filters.get("status"))
	elif not filters.get("status"):
		columns.append({"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "120"})
	query = """ SELECT * FROM `tabProduction` WHERE docstatus = 1 {0} ORDER BY posting_date ASC""".format(conditions)
	production = frappe.db.sql(query, as_dict=1)

	return columns, production
