// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Landed Cost Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			// "reqd":1,
		
		},
		{			
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",
			// "reqd":1,		
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": "Item Code",
			"options":"Item",
			// "reqd":1,
		
		},
		{
			"fieldname": "price_list",
			"fieldtype": "Link",
			"label": "price List",
			"options":"Price List",
			"get_query": function() {
				return {
					"doctype": "Price List",
					"filters": {
						"selling": 1
					}
				};
			}
		
		},
		{			
			"fieldname": "supplier",
			"fieldtype": "Link",
			"label": "Supplier",
			"options": "Supplier",
			// "reqd":1,		
		},


		{			
			"fieldname": "item_group",
			"fieldtype": "Link",
			"label": "Item Group",
			"options": "Item Group",
			// "reqd":1,		
		},

	]
};