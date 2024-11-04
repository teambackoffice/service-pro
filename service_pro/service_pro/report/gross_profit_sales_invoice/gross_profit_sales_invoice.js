// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

frappe.query_reports["Gross Profit Sales Invoice"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
			reqd: 1,
		},
		{
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Link",
			options: "Sales Invoice",
			
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options:
				"Invoice\nItem Code\nItem Group\nBrand\nWarehouse\nCustomer\nCustomer Group\nTerritory\nSales Person\nProject\nCost Center\nMonthly\nPayment Term",
			default: "Invoice",
			read_only: 1
		},
		{
			fieldname: "sales_man",
			label: __("Sales Man"),
			fieldtype: "Link",
			options: "Sales Man",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("Cost Center", txt, {
					company: frappe.query_report.get_filter_value("company"),
				});
			},
		},
	],
	tree: true,
	name_field: "parent",
	parent_field: "parent_invoice",
	initial_depth: 3,
	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname == "sales_invoice" && column.options == "Item" && data && data.indent == 0) {
			column._options = "Sales Invoice";
		} else {
			column._options = "";
		}
		value = default_formatter(value, row, column, data);

		if (data && (data.indent == 0.0 || (row[1] && row[1].content == "Total"))) {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
};

erpnext.utils.add_dimensions("Gross Profit", 15);
