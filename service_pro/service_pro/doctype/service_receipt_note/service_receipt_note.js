// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Receipt Note', {
	refresh: function(frm) {

        if(cur_frm.doc.docstatus){
            frappe.db.get_list('Inspection', {
                fields: ["*"],
                filters: {
                    service_receipt_note: cur_frm.docname,
                    docstatus: 0
                }
            }).then(records => {
                if(records.length > 0){
                    frm.add_custom_button(__("Submit Inspection/s"), () => {
                        frappe.confirm('Are you sure you want to submit Inspections?',
                            () => {
                                 frm.call({
                                    doc: frm.doc,
                                    method: 'submit_inspections',
                                    freeze: true,
                                    freeze_message: "Submitting Inspections...",
                                    callback: () => {
                                        cur_frm.refresh()
                                    }
                                })
                            }, () => {
                                // action to perform if No is selected
                            })

                    });
                }
            })
        }
	}
});
