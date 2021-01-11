# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
def get_columns():
	return [
			{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "100"},
			{"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Data", "width": "150"},
			{"label": "PO No", "fieldname": "po_no", "fieldtype": "Data", "width": "150"},
			{"label": "Debit", "fieldname": "debit_in_account_currency", "fieldtype": "Currency", "width": "100"},
			{"label": "Credit", "fieldname": "credit_in_account_currency", "fieldtype": "Currency", "width": "100"},
			{"label": "Balance", "fieldname": "balance", "fieldtype": "Currency","width": "100"},
		]

def execute(filters=None):
	columns, data = get_columns(), []

	condition = ""

	if filters.get("from_date") and filters.get("to_date"):
		condition += " WHERE posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("customer"):
		if not condition:
			condition += " WHERE "
		else:
			condition += " and "
		condition += " against='{0}'".format(filters.get("customer"))

	print(condition)
	query = """ SELECT * FROM `tabGL Entry` {0}""".format(condition)
	print(query)
	gl_entries = frappe.db.sql(query,as_dict=1)
	for i in gl_entries:
		if i.voucher_type == "Sales Invoice":
			si = frappe.db.sql(""" SELECT * FROM `tabSales Invoice` WHERE name=%s """, i.voucher_no, as_dict=1)
			if len(si) > 0:
				i['po_no'] = si[0].po_no
		i['balance'] = i.debit_in_account_currency - i.credit_in_account_currency
		data.append(i)
	return columns, data
