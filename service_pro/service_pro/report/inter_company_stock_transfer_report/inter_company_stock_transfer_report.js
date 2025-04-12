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
       
    ]
};
