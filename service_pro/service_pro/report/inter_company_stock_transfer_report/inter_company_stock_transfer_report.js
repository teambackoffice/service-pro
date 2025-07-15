

frappe.query_reports["Inter Company Stock Transfer Report"] = {
    tree: true,
    name_field: "name",
    parent_field: "parent_transfer",
    initial_depth: 1,
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "posting_date",
            label: __("Posting Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "from_company",
            label: __("From Company"),
            fieldtype: "Link",
            options: "Company",
        },
        {
            fieldname: "to_company",
            label: __("To Company"),
            fieldtype: "Link",
            options: "Company",
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: ["", "Draft", "Received", "Cancelled"],
        },
        {
            fieldname: "name",
            label: __("ID"),
            fieldtype: "Data"
        }
    ]
};
