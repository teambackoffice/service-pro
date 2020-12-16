// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Statement of Account"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "party",
			"label": __("Supplier Name"),
			"fieldtype": "Link",
			"options" : "Supplier",
			"reqd": 1
		},
		{
			"fieldname": "show_foreign_currency",
			"label":__("Show Foreign Currency"),
			"fieldtype": "Check",
		}

	]
};
