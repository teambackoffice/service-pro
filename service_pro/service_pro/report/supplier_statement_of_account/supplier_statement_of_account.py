# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext

def execute(filters=None):
	columns, data = [], []
	conditions = ""	

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("party"):
		conditions += " and party='{0}' ".format(filters.get("party"))

	if filters.get("show_foreign_currency"):
		conditions += " and PI.grand_total='{0}'".format(filters.get("grand_total"))
	
	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": "120"},
		{"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Link", "options": "Purchase Invoice", "width": "200"},
		{"label": "Debit (SAR)", "fieldname": "debit", "fieldtype": "Float", "width": "110"},
		{"label": "Credit (SAR)", "fieldname": "credit", "fieldtype": "Float", "width": "110"},
		{"label": "Balance (SAR)", "fieldname": "balances", "fieldtype": "Float", "width": "110"},
		{"label": "Foreign Currency", "fieldname": "grand_total", "fieldtype": "Float", "width": "130"},
	]
	query = """ SELECT * FROM `tabGL Entry`  WHERE docstatus= 1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)
	for i in data:
		i["debit_balances"] = i.debit
		i["credit_balances"] = -i.credit
		i["balances"] = i.credit_balances + i.debit_balances

	return columns, data
