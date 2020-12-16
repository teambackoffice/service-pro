// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Checkin Register"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee Name"),
			"fieldtype":"Link",
			"options": "Employee",
		},
		{
			"fieldname": "from_time",
			"label":__("From Time"),
			"fieldtype": "Datetime",
			"options": "Employee Checkin",
		},
		{
			"fieldname": "to_time",
			"label":__("To Time"),
			"fieldtype": "Datetime",
			"options": "Employee Checkin",
		},
	]
};
