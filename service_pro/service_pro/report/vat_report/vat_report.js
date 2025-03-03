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
			fieldname:"sales_or_purchase",
			label: __("Sales or Purchase"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
                if (!frappe.query_report.filters) return;

                return [{value: "Sales", description: ""}, {value: "Purchase", description: ""}]
            },
			on_change: function (txt) {
				console.log("teeeest")
				frappe.query_report.refresh()
            }
		},
		{
			"fieldname": "company",
            "label": __("company"),
            "fieldtype": "Link",
			"options": "Company",
		},
		{
			fieldname: "summery",
            label: __("Summery"),
            fieldtype: "Check"
		}
	]
};
