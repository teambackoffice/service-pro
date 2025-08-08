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
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;

				return [
					{value: "Sales", description: "Sales Invoice"},
					{value: "Purchase", description: "Purchase Invoice"},
					{value: "Expense Claim", description: "Expense Claim"},
					{value: "Journal Entry", description: "Journal Entry"}
				]
			},
			on_change: function (txt) {
				console.log("Sales/Purchase/Expense Claim/Journal Entry filter changed");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 0,
			on_change: function() {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "summery",
			label: __("Summary"),
			fieldtype: "Check"
		}
	]
};