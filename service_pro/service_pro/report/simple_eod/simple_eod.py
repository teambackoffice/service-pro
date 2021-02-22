# Copyright (c) 2013, Sammish Thundiyil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	condition = ""

	if filters.get("from_date") and filters.get("to_date"):
		condition += " and posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("account"):
		condition += " and account='{0}'".format(filters.get("account"))

	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": "110"},
		{"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Data", "width": "180"},
		{"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": "180"},
		{"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": "110"},
		{"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": "110"},
		{"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": "110"},
	]
	query = """ SELECT * FROM `tabGL Entry` WHERE docstatus= 1 {0}""".format(condition)
	data = frappe.db.sql(query, as_dict=1)
	for i in data:
    		i["balance"] = i.debit - i.credit

	return columns, data
