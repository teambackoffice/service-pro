// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock List Report"] = {
	"filters": [
		{
			fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
		},
		{
			fieldname: "ignore_zero_stock",
            label: __("Ignore Zero Stock"),
            fieldtype: "Check"
		},
		{
			fieldname: "ignore_negative_stock",
            label: __("Ignore Negative Stock"),
            fieldtype: "Check"
		}
	]
};
