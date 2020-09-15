// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Agent Payment Request', {
	refresh: function(frm) {
        document.querySelectorAll("[data-doctype='Journal Entry']")[1].style.display ="none";

	    var show = false
        frappe.call({
            method: "service_pro.service_pro.doctype.agent_payment_request.agent_payment_request.get_jv",
            args:{
                name: cur_frm.doc.name
            },
            async: false,
            callback: function (r) {
                show = r.message
                console.log(r.message)
            }
        })
	    if(cur_frm.doc.docstatus && !show){
	         frm.add_custom_button(__("Journal Entry"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'generate_journal_entry',
                        args: {},
                        freeze: true,
                        freeze_message: "Generating Journal Entry...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                                frappe.set_route("Form", "Journal Entry", r.message);
                        }
                })
            }, "Generate")
        }


	}
});
