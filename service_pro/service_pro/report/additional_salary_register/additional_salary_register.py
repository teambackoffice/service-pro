# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and payroll_date BETWEEN '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("employee"):
		conditions += " and employee='{0}' ".format(filters.get("employee"))

	if filters.get("salary_component"):
		conditions += " and salary_component='{0}' ".format(filters.get("salary_component"))

	columns = [
		{"label": "Payroll Date", "fieldname": "payroll_date", "fieldtype": "Data", "width": "100"},
		{"label": "Name", "fieldname": "name", "fieldtype": "Link", "options": "Additional Salary", "width": "150"},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Link", "options": "Employee", "width": "250"},
		{"label": "Additional", "fieldname": "salary_component", "fieldtype": "Link", "options": "Salary Component", "width": "200"},
		{"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": "100"},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Data", "width": "80"},
	]
	query = """ SELECT * FROM `tabAdditional Salary` WHERE docstatus=1 {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)

	return columns, data
