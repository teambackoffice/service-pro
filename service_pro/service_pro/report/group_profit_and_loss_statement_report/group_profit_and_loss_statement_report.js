// Copyright (c) 2025, jan and contributors
// For license information, please see license.txt
frappe.query_reports["Group Profit and Loss Statement Report"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Group Profit and Loss Statement Report", 10);

frappe.query_reports["Group Profit and Loss Statement Report"]["filters"].push({
    fieldname: "selected_view",
    label: __("Select View"),
    fieldtype: "Select",
    options: [
        { value: "Report", label: __("Report View") },
        { value: "Growth", label: __("Growth View") },
        { value: "Margin", label: __("Margin View") },
    ],
    default: "Report",
    reqd: 1,
});

frappe.query_reports["Group Profit and Loss Statement Report"]["filters"].push({
    fieldname: "accumulated_values",
    label: __("Accumulated Values"),
    fieldtype: "Check",
    default: 1,
});

frappe.query_reports["Group Profit and Loss Statement Report"]["filters"].push({
    fieldname: "include_default_book_entries",
    label: __("Include Default FB Entries"),
    fieldtype: "Check",
    default: 1,
});
