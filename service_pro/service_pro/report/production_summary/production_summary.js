// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Summary"] = {
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
			fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nIn Progress\nPartially Delivered\nCompleted\nTo Deliver and Bill\nTo Deliver\nTo Bill\nClosed\nLinked",
		}
	]
};
