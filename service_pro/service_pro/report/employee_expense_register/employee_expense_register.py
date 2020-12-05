# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("employee"):
		conditions += " and employee='{0}' ".format(filters.get("employee"))

	if filters.get("status"):
		conditions += "and status='{0}' ".format(filters.get("status"))
	elif not filters.get("status"):
		columns.append({"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "80"})

	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Link", "options": "Expense Claim", "width": "100"},
		{"label": "Expense Claim", "fieldname": "name", "fieldtype": "Link", "options": "Expense Claim", "width": "150"},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Link", "options": "Expense Claim", "width": "250"},
		{"label": "Claimed", "fieldname": "total_claimed_amount", "fieldtype": "Data", "width": "80"},
		{"label": "Sanctioned", "fieldname": "total_sanctioned_amount", "fieldtype": "Data", "width": "110"},
		{"label": "Advance", "fieldname": "total_advance_amount", "fieldtype": "Data", "width": "80"},
		{"label": "Reimbursed", "fieldname": "total_amount_reimbursed", "fieldtype": "Data", "width": "110"},
		{"label": "Total", "fieldname": "grand_total", "fieldtype": "Data", "width": "110"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "80"},
	]
	query = """ SELECT * FROM `tabExpense Claim` WHERE docstatus=1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)

	return columns, data