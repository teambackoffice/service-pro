// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Order Requisition for Average Stocks"] = {
	"filters": [
		{
			fieldname: "average_stock",
            label: __("Average Stock"),
            fieldtype: "Select",
			options: ['January-June', 'July-December'],
			reqd:1
		},
		{
			fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
			options: "Item Group",
			reqd: 1
		},
		{
			fieldname: "item",
            label: __("Item"),
            fieldtype: "Link",
			options: "Item"
		}
	]
};
