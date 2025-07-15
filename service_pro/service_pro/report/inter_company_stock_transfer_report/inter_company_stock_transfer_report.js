// frappe.query_reports["Your Report Name"] = {
//   filters: [
//     {
//       fieldname: "from_company",
//       label: __("From Company"),
//       fieldtype: "Link",
//       options: "Company"
//     },
//     {
//       fieldname: "to_company",
//       label: __("To Company"),
//       fieldtype: "Link",
//       options: "Company"
//     },
//     {
//       fieldname: "name",
//       label: __("Transfer ID"),
//       fieldtype: "Link",
//       options: "Inter Company Stock Transfer"
//     },
//     {
//       fieldname: "status",
//       label: __("Status"),
//       fieldtype: "Select",
//       options: "\nDraft\nSubmitted\nCancelled"
//     },
//     {
//       fieldname: "from_date",
//       label: __("From Date"),
//       fieldtype: "Date",
//       default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
//       reqd: 1
//     },
//     {
//       fieldname: "to_date",
//       label: __("To Date"),
//       fieldtype: "Date",
//       default: frappe.datetime.get_today(),
//       reqd: 1
//     }
//   ],

//   tree: true,
//   name_field: "name",
//   parent_field: "parent_transfer",
//   initial_depth: 1,

//   formatter: function(value, row, column, data, default_formatter) {
//     value = default_formatter(value, row, column, data);
//     if (data && data.indent === 0) {
//       value = `<b>${value}</b>`;
//     }
//     return value;
//   }
// };
frappe.query_reports["Inter Company Transfer Report"] = {
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
            options: ["", "Draft", "Submitted", "Cancelled"],
        }
    ]
};
