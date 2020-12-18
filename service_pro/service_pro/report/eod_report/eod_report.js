// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["EOD Report"] = {
	"filters": [
		{
			fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
            reqd: 1,
		},{
			"fieldname":"mop",
			"label": __("MOP"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
                if (!frappe.query_report.filters) return;

                return [{value: "Showroom Cash", description: ""}, {value: "Showroom Card", description: ""}]
            }
		}
	]
};
