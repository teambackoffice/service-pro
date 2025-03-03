// Copyright (c) 2025, jan and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Register Summary Company"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label":__("Customer Name"),
			"fieldtype":"Link",
			"options": "Customer",
		},
		{
			"fieldname": "cost_center",
			"label":__("Cost Center"),
			"fieldtype":"Link",
			"options": "Cost Center",
		},
		{
			"fieldname": "status",
			"label":__("Satatus"),
			"fieldtype": "Select",
			"options": "\nPaid\nUnpaid\nOverdue",
		},
		{
			"fieldname": "paid_disabled",
            "label": __("Paid Disabled"),
            "fieldtype": "Check",
		},
		{
			"fieldname": "company",
            "label": __("company"),
            "fieldtype": "Link",
			"options": "Company",
		}
	]
};

