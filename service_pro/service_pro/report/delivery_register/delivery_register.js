// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype":"Date",
		},
		{
			"fieldname": "customer",
			"label":__("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "sales_man",
			"label":__("Sales Man Name"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "status",
			"label":__("Status"),
			"fieldtype": "Select",
			"options": "\nTo Bill\nCompleted\nClosed",
		}
	]
};
