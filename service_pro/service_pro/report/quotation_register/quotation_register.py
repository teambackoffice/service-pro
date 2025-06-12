# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and q.transaction_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("party_name"):
		conditions += " and q.party_name='{0}' ".format(filters.get("party_name"))

	if filters.get("custom_sales_person"):
		conditions += " and q.custom_sales_person='{0}' ".format(filters.get("custom_sales_person"))

	if filters.get("status"):
		conditions += " and q.status='{0}' ".format(filters.get("status"))

	columns = [
		{"label":"Posting Date", "fieldname":"transaction_date", "fieldtype":"Link", "options":"Quotation", "width": "100"},
		{"label":"Series", "fieldname":"name", "fieldtype":"Link", "options":"Quotation", "width": "160"},
		{"label":"Customer Name", "fieldname":"customer_name", "fieldtype":"Link", "options":"Quotation", "width": "280"},
		{"label":"Sales Person", "fieldname":"sales_person_name", "fieldtype":"Data", "width": "180"},
		{"label":"Total", "fieldname":"total", "fieldtype":"Data", "width": "80"},
		{"label":"Discount", "fieldname":"discount_amount", "fieldtype":"Data", "width": "80"},
		{"label":"Net Total", "fieldname":"net_total", "fieldtype":"Data", "width": "80"},
		{"label":"VAT", "fieldname":"total_taxes_and_charges", "fieldtype":"Data", "width": "80"},
		{"label":"Grand Total", "fieldname":"grand_total", "fieldtype":"Data", "width": "100"},
		{"label":"Status", "fieldname":"status", "fieldtype":"Data", "width": "80"},
	]
	
	query = """
		SELECT 
			q.*,
			sp.sales_person_name as sales_person_name
		FROM `tabQuotation` q
		LEFT JOIN `tabSales Person` sp ON q.custom_sales_person = sp.name
		WHERE q.docstatus=1 {0}
	""".format(conditions)
	
	data = frappe.db.sql(query, as_dict=1)

	return columns, data
