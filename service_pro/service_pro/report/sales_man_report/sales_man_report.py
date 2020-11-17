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


	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Link", "options": "Production", "width": "100"},
		{"label": "Sales Invoice", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": "130"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "280"},
		{"label": "Net Total", "fieldname": "total", "fieldtype": "Data", "width": "100"},
		{"label": "VAT", "fieldname": "total_taxes_and_charges", "fieldtype": "Data", "width": "100"},
		{"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Data", "width": "100"},
		{"label": "Agent Commission", "fieldname": "incentive", "fieldtype": "Data", "width": "150"},
	]
	query = """ SELECT * FROM `tabSales Invoice` WHERE docstatus=1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)

	return columns, data
