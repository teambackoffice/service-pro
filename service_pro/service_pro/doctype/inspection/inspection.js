// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inspection', {
     customer: function () {
	    if(cur_frm.doc.customer){
	         frappe.db.get_doc("Customer", cur_frm.doc.customer)
            .then(doc => {
                cur_frm.doc.customer_name = doc.customer_name
                cur_frm.refresh_field("customer_name")
            })
        }

    },
	// refresh: function(frm) {
     //    if(cur_frm.is_new()){
     //         frm.add_custom_button(__("Service Receipt Note"), () => {
     //                    get_items_from_srn(cur_frm)
     //                }, __("Get Items From"))
     //    }
	// }
});

function get_items_from_srn(cur_frm) {
    new frappe.ui.form.MultiSelectDialog({
        doctype: "Service Receipt Note Item",
        target: cur_frm,
        setters: {},
        date_field: "posting_date",
        get_query() {
            return {
                filters: { docstatus: ['!=', 2] }
            }
        },
        action(selections) {
            console.log(selections);
        }
    });

// MultiSelectDialog with custom query method
// let query_args = {
//     query:"dotted.path.to.method",
//     filters: { docstatus: ["!=", 2], supplier: "John Doe" }
// }
//
// new frappe.ui.form.MultiSelectDialog({
//     doctype: "Material Request",
//     target: this.cur_frm,
//     setters: {
//         company: "Zoot"
//     },
//     date_field: "transaction_date",
//     get_query() {
//         return query_args;
//     },
//     action(selections) {
//         console.log(selections);
//     }
// });
}

cur_frm.cscript.item_code = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
     frappe.db.get_doc("Item", d.item_code)
            .then(doc => {
               d.item_name = doc.item_name
                cur_frm.refresh_field("item_name")
            })
}
