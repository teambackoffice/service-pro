// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Simple EOD"] = {
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
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "Select",
			"options" : "\n1351 - Showroom Accrual - Cash - HT\n1352 - Showroom Accrual - Card - HT",
			"reqd": 1
		}
	]
};
