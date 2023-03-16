// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["OMFB Item Report"] = {
	"filters": [
		{
		 "fieldname": "posting_date",
		 "fieldtype": "Date",
		 "label": "Posting Date",
		//  "reqd": 1
		},
		{
		 "fieldname": "customer",
		 "fieldtype": "Link",
		 "options":"Customer",
		 "label": "Customer",
		//  "reqd": 1
		},
		{
		 "fieldname": "supplier",
		 "fieldtype": "Link",
		//  "in_list_view": 1,
		 "label": "Supplier",
		 "options":"Supplier",
		 // "reqd": 1
		},
		{
		 "fieldname": "item",
		 "fieldtype": "Link",
		 "in_list_view": 1,
		 "label": "Item",
		 "options":"Item",
		//  "reqd": 1
		 
		},
	]
};
