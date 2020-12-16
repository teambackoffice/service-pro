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
		conditions += " and status = '{0}'".format(filters.get("status"))
	elif not filters.get("status"):
		columns.append({"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": "80"})

	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Link", "options": "Employee Advance", "width": "100"},
		{"label": "Employee Advance", "fieldname": "name", "fieldtype": "Link", "options": "Employee Advance", "width": "200"},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Link", "options": "Employee Advance", "width": "250"},
		{"label": "Advance", "fieldname": "advance_amount", "fieldtype": "Data", "options": "Employee Advance", "width": "80"},
		{"label": "Paid", "fieldname": "paid_amount", "fieldtype": "Data", "options": "Employee Advance", "width": "80"},
		{"label": "Claimed ", "fieldname": "claimed_amount", "fieldtype": "Data", "options": "Employee Advance", "width": "80"},
		{"label": "Return ", "fieldname": "return_amount", "fieldtype": "Data", "options": "Employee Advance", "width": "80"},
		{"label": "Balance ", "fieldname": "balance", "fieldtype": "Data", "width": "80"},
		{"label": "Status ", "fieldname": "status", "fieldtype": "Data", "options": "Employee Advance", "width": "80"},
	]
	query = """ SELECT * FROM `tabEmployee Advance` WHERE docstatus=1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)
	for i in data:
		i["balance"] = i.paid_amount - i.return_amount - i.claimed_amount if i.return_amount or i.claimed_amount > 0 else i.paid_amount

	return columns, data


