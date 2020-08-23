// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Cash Book"] = {
	"filters": [
{
			fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
		},
		{
			fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
		},
		{
			fieldname: "pos_profile",
            label: __("POS Profile"),
            fieldtype: "Link",
            options: "POS Profile",
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;
				return frappe.db.get_link_options("Cost Center", txt);
			},
		},
		{
			fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse",
		},
		{
			"fieldname":"mop",
			"label": __("MOP"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;
				return frappe.db.get_link_options("Mode of Payment", txt);
			},
		},
		{
			fieldname: "paid_disabled",
            label: __("Paid Disabled"),
            fieldtype: "Check",
		},
	]
};
