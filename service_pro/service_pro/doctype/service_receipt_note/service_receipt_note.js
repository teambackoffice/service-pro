// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Receipt Note', {

	refresh: function(frm) {
        if (cur_frm.doc.docstatus) {
            frm.add_custom_button(__('Inspection'), () => {
                frappe.new_doc('Inspection', {
                    service_receipt_note: frm.doc.name,
                    customer: frm.doc.customer,
                    customer_name: frm.doc.customer_name,
                    company: frm.doc.company,
                });
            }, __('Create'));
        }
cur_frm.set_query("customer", () => {
            return {
                filters: {
                    disabled: 0
                }
            }
        })
	    frm.set_query("contact_person", function(){
            if(frm.doc.customer) {
                return {
                    filters: {
                        link_doctype: "Customer",
                        link_name: frm.doc.customer
                    }
                };
           }
        });

        if(cur_frm.doc.docstatus && !(["Closed", "Completed"].includes(cur_frm.doc.status))){
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

            frappe.db.get_list('Inspection', {
                fields: ["*"],
                filters: {
                    service_receipt_note: cur_frm.docname,
                    docstatus: 0
                }
            }).then(records => {
                if(records.length > 0){

                    // frm.add_custom_button(__("Submit Inspection/s"), () => {
                    //     submit_inspections(frm, cur_frm)
                    // }, __("Submit"))
                }
            })

             frappe.db.get_list('Estimation', {
                fields: ["*"],
                filters: {
                    receipt_note: cur_frm.docname,
                    docstatus: 0
                }
            }).then(records => {
                if(records.length > 0){

                    // frm.add_custom_button(__("Submit Estimation/s"), () => {
                    //     submit_estimations(frm, cur_frm)

                    // }, __("Submit"))
                }
            })
                 frappe.db.get_list('Quotation', {
                    fields: ["*"],
                    filters: {
                        service_receipt_note: cur_frm.docname,
                    }
                }).then(records => {
                    if(records.length === 0){
                        frappe.db.get_list('Estimation', {
                            fields: ["*"],
                            filters: {
                                receipt_note: cur_frm.docname,
                                docstatus: 0
                            }
                        }).then(records1 => {
                            if(records1.length === 0){
                               frappe.db.get_list('Inspection', {
                                    fields: ["*"],
                                    filters: {
                                        service_receipt_note: cur_frm.docname,
                                        docstatus: 0
                                    }
                                })
                                // .then(records2 => {
                                //     if(records2.length === 0){
                                //        frm.add_custom_button(__("Quotation"), () => {
                                //             create_quotation(frm, cur_frm)

                                //         }, __("Create"))
                                //     }
                                // })
                            }
                        })
                    }
                })


        } else if (cur_frm.doc.status === "Closed"){
            frm.add_custom_button(__("Open"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "To Inspection"
                        },
                        freeze: true,
                        freeze_message: "Opening...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
        }
	},
    customer: function () {
	    if(cur_frm.doc.customer){
	         frappe.db.get_doc("Customer", cur_frm.doc.customer)
            .then(doc => {
                cur_frm.doc.customer_name = doc.customer_name
                cur_frm.refresh_field("customer_name")
            })
        }

    },
    contact_person: function () {
	    if(cur_frm.doc.contact_person){
	         frappe.db.get_doc("Contact", cur_frm.doc.contact_person)
                .then(doc => {
                    console.log(doc)
                    for(var x=0;x<doc.phone_nos.length;x+=1){
                        if(doc.phone_nos[x].is_primary_phone){
                            cur_frm.doc.contact_number = doc.phone_nos[x].phone
                            cur_frm.refresh_field("contact_number")
                        }
                    }
                })
        }

    },
    sales_man: function () {
	    if(cur_frm.doc.sales_man){
	         frappe.db.get_doc("Employee", cur_frm.doc.sales_man)
                .then(doc => {

                        cur_frm.doc.sales_man_name = doc.employee_name
                        cur_frm.refresh_field("sales_man_name")

                })
        }

    }
});

function submit_inspections(frm, cur_frm) {
    frappe.confirm('Are you sure you want to submit Inspection/s?',
        () => {
             frm.call({
                doc: frm.doc,
                method: 'submit_inspections',
                freeze: true,
                freeze_message: "Submitting Inspection/s...",
                callback: () => {
                    cur_frm.refresh()
                }
            })
        }, () => {
            // action to perform if No is selected
    })
}

function submit_estimations(frm, cur_frm) {
    frappe.confirm('Are you sure you want to submit Estimation/s?',
        () => {
             frm.call({
                doc: frm.doc,
                method: 'submit_estimations',
                freeze: true,
                freeze_message: "Submitting Estimation/s...",
                callback: () => {
                    cur_frm.reload_doc()
                }
            })
        }, () => {
            // action to perform if No is selected
        })
}

function create_quotation(frm, cur_frm) {
    frm.call({
        doc: frm.doc,
        method: 'create_quotation',
        freeze: true,
        freeze_message: "Creating Quotation...",
        callback: (r) => {

            frappe.set_route('Form', 'Quotation', r.message)

        }
    })
    // frappe.model.open_mapped_doc({
    //     method: "service_pro.service_pro.doctype.service_receipt_note.service_receipt_note.make_quotation",
    //     frm: me.frm
    // })
}
cur_frm.cscript.materials = function (frm, cdt, cdn) {

    var d = locals[cdt][cdn]
    if(d.materials){
       frappe.db.get_doc("Item", d.materials)
            .then(doc => {
               d.item_name = doc.item_name
                cur_frm.refresh_field("materials")
            })
    }

}