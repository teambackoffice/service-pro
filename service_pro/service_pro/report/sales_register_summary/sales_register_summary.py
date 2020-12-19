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

	if filters.get("status"):
		conditions += " and status='{0}' ".format(filters.get("status"))

	if filters.get("cost_center"):
		conditions += " and cost_center='{0}' ".format(filters.get("cost_center"))

	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "100"},
		{"label": "Name", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": "150"},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer", "width": "250"},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": "150"},
        {"label": "Net Total", "fieldname": "net_total", "fieldtype": "currency", "width": "80"},
        {"label": "VAT ", "fieldname": "total_taxes_and_charges", "fieldtype": "currency", "width": "80"},
        {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "currency", "width": "100"},
		{"label": "Outstanding", "fieldname": "outstanding_amount", "fieldtype": "party_account_currency", "width": "100"},
		{"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Data", "width": "100"},	
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "100"},
	]
	query = """ SELECT * FROM `tabSales Invoice` WHERE docstatus=1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)
	for i in data:
		i["paid_amount"] = i.grand_total - i.outstanding_amount if i.grand_total  > 0 else i.outstanding_amount

	return columns, data
