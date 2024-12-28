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
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Estimation'), function () {
                frappe.call({
                    method: "service_pro.service_pro.doctype.inspection.inspection.create_production",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.set_route("Form", "Estimation", r.message.name);
                        }
                    }
                });
            }, __("Create"));
            
            }


        cur_frm.set_query('service_receipt_note', () => {
            return {
                filters: [
                    ["docstatus", "=", 1],
                    ["status", "=", "To Inspection"]
                ]
            }
        })
        if(cur_frm.doc.docstatus && !(["Closed", "Completed"].includes(cur_frm.doc.status))){
            console.log("WALA MAN")
             frm.add_custom_button(__("Close"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "Closed"
                        },
                        freeze: true,
                        freeze_message: "Closing...",
                        callback: () => {
                            cur_frm.reload_doc()
                        }
                })
            })
        } else if (cur_frm.doc.status === "Closed"){
            frm.add_custom_button(__("Open"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "To Estimation"
                        },
                        freeze: true,
                        freeze_message: "Opening...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
        }
    }
});


cur_frm.cscript.item_code = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
     frappe.db.get_doc("Item", d.item_code)
            .then(doc => {
               d.item_name = doc.item_name
                cur_frm.refresh_field("item_name")
            })
}
