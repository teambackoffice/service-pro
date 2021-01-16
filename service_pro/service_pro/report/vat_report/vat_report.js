// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["VAT Report"] = {
	"filters": [
		{
			fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1
		},
		{
			fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
			reqd: 1

		},
		{
			fieldname: "sales_or_purchase",
            label: __("Sales or Purchase"),
            fieldtype: "Select",
            options: ['Sales', 'Purchase'],
			reqd: 1
		},
		{
			fieldname: "summery",
            label: __("Summery"),
            fieldtype: "Check"
		}
	]
};
