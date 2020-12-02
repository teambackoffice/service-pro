// Copyright (c) 2016, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Additional Salary Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",

		},
		{
			"fieldname": "employee",
			"label":__("Employee Name"),
			"fieldtype":"Link",
			"options": "Employee",
		},
		{
			"fieldname": "salary_component",
			"label":__("Additional"),
			"fieldtype": "Select",
			"options": "\nSalary Advance 1St\nSalary Advance 2nd\nSalary Advance 3rd\nOver Time\nAbsent Deduction",
		}
	]	
};
