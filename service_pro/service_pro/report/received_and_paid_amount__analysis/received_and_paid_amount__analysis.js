// Copyright (c) 2022, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Received and Paid Amount  Analysis"] = {
	"filters": [
		{
			fieldname: "payment_type",
            label: __("Payment Type"),
            fieldtype: "Select",
		},
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
			fieldname: "party_type",
            label: __("Party Type"),
            fieldtype: "Link",
            options: "DocType",
		},
		{
			fieldname: "mode_of_payment",
            label: __("Mode of Payment"),
            fieldtype: "Link",
            options: "Mode of Payment",
		},
	]
};
