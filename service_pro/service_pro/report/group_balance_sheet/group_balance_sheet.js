frappe.query_reports["Group Balance Sheet"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Group Balance Sheet", 10);

frappe.query_reports["Group Balance Sheet"]["filters"].push(
  {
    fieldname: "selected_view",
    label: __("Select View"),
    fieldtype: "Select",
    options: [
      { value: "Report", label: __("Report View") },
      { value: "Growth", label: __("Growth View") },
    ],
    default: "Report",
    reqd: 1,
  },
  {
    fieldname: "accumulated_values",
    label: __("Accumulated Values"),
    fieldtype: "Check",
    default: 1,
  },
  {
    fieldname: "include_default_book_entries",
    label: __("Include Default FB Entries"),
    fieldtype: "Check",
    default: 1,
  },
  {
    fieldname: "accumulated_in_group_company",
    label: __("Accumulate Group Companies"),
    fieldtype: "Check",
    default: 1,
  }
);
