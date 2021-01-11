// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statement of Account"] = {
	"filters": [
		{
			fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
		},
		{
			fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
			            reqd: 1,

		},
		{
			fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer",
		}

	]
};
