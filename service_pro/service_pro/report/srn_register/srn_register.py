# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("status"):
		conditions += " and status='{0}'".format(filters.get("status"))

	if filters.get("customer"):
		conditions += " and customer='{0}'".format(filters.get("customer"))

	if filters.get("sales_man"):
		conditions += " and sales_man='{0}'".format(filters.get("sales_man"))

	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": "100"},
		{"label": "Estimated Date", "fieldname": "estimated_date", "fieldtype": "Data", "width": "100"},
		{"label": "Serial No", "fieldname": "name", "fieldtype": "Link", "options": "Service Receipt Note", "width": "120"},
		{"label": "Sales Man Name", "fieldname": "sales_man_name", "fieldtype": "Data", "width": "200"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer", "width": "280"},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Link", "options": "Item", "width": "120"},
		{"label": "QTY", "fieldname": "qty", "fieldtype": "Float", "width": "50"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Select", "width": "100"},
	]
	query = """ SELECT 
 					A.posting_date, 
 					A.estimated_date,
					A.name,
 					A.customer_name,
					A.sales_man_name,
					A.status,
					B.item_name,
					B.qty
				FROM 
					`tabService Receipt Note` AS A,
					`tabService Receipt Note Item` AS B 
				WHERE A.docstatus = 1 {0}""".format(conditions)
	
	data = frappe.db.sql(query,as_dict=1)
	
	return columns, data
