// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Man Report"] = {
	"filters": [
{
			fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
		},
		{
			fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
		},
		{
			fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer",
		},
		{
			fieldname: "sales_man",
            label: __("Sales Man"),
            fieldtype: "Link",
            options: "Employee",
		},
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "MultiSelectList",
            get_data: function (txt) {
                if (!frappe.query_report.filters) return;

                return [{value: "Paid", description: ""}, {value: "Unpaid", description: ""}, {
                    value: "Overdue",
                    description: ""
                }]
            },
            "on_change": function (txt) {
                frappe.query_report.refresh()
            }
        }
	]
};
