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

	if filters.get("sales_man"):
		conditions += " and sales_man='{0}' ".format(filters.get("sales_man"))

	if filters.get("status"):
		conditions += " and status='{0}' ".format(filters.get("status"))

	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": "100"},
		{"label": "Serial No", "fieldname": "name", "fieldtype": "Link", "options": "Delivery Note", "width": "150"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer", "width": "300"},
		{"label": "Sales Man", "fieldname": "sales_man_name", "fieldtype": "Data", "width": "200"},
		{"label": "VAT Amount", "fieldname": "total_taxes_and_charges", "fieldtype": "Data", "width": "100"},
		{"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Data", "width": "100"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "100"},

	]
	query = """ SELECT * FROM `tabDelivery Note` WHERE status=0 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)

	return columns, data