// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Expense Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label":__("To Date"),
			"fieldtype":"Date",
		},
		{
			"fieldname": "to_date",
			"label":__("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "employee",
			"label":__("Employee Name"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "status",
			"label":__("Status"),
			"fieldtype": "Select",
			"options": "\nPaid\nUnpaid",
		}

	]
};
