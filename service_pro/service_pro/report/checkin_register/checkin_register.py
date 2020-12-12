# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	conditions = ""

	if filters.get("employee"):
		conditions += " and employee='{0}' ".format(filters.get("employee"))

	if filters.get("from_time") and filters.get("to_time"):
		conditions += " and time BETWEEN '{0}' and '{1}'".format(filters.get("from_time"),filters.get("to_time"))

	columns = [
		{"label": "Date and Time", "fieldname": "time", "fieldtype": "Datetime", "width": "180"},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Link", "options": "Employee","width": "250"},
		{"label": "Location", "fieldname": "device_id", "fieldtype": "Data", "width": "120"},
		{"label": "Log Type", "fieldname": "log_type", "fieldtype": "Data", "width": "80"},
	]
	query = """ SELECT * FROM `tabEmployee Checkin` WHERE docstatus='log_type' {0}""".format(conditions)
	data = frappe.db.sql(query, as_dict=1)

	return columns, data