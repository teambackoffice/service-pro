frappe.query_reports["Inter Company Stock Transfer Report"] = {
    filters: [
        {
            fieldname: "from_company",
            label: __("From Company"),
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "to_company",
            label: __("To Company"),
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "name",
            label: __("ID"),
            fieldtype: "Link",
            options: "Inter Company Stock Transfer"
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nDraft\nCompleted\nIn Transit\nReceived",
        },
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
    ]
};
