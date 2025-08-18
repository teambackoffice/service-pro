// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["Bank Balance Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				return {
					"filters": {
						"account_type": ["like", "%Bank%"],
						"is_group": 0,
						"disabled": 0
					}
				}
			}
		},
		{
			"fieldname": "include_opening",
			"label": __("Include Opening Entries"),
			"fieldtype": "Check",
			"default": 0
		}
	],
	
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "balance") {
			if (data && data.balance) {
				if (data.balance > 0) {
					value = "<span style='color:green'>" + value + "</span>";
				} else if (data.balance < 0) {
					value = "<span style='color:red'>" + value + "</span>";
				}
			}
		}
		
		if (column.fieldname == "name" && data && data.name) {
			value = "<a href='#Form/Account/" + data.name + "'>" + value + "</a>";
		}
		
		return value;
	},
	
	"onload": function(report) {
		report.page.add_inner_button(__("Export to Excel"), function() {
			frappe.tools.downloadify(report.data, null, report.report_name);
		});
		
		report.page.add_inner_button(__("Print"), function() {
			report.print_report();
		});
	}
};