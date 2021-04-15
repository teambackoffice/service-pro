// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Agent Payment Request', {
	claim_amount: function(frm) {
	    cur_frm.doc.agent_outstanding_amount = cur_frm.doc.claim_amount
        cur_frm.refresh_field("agent_outstanding_amount")
    },
	refresh: function(frm) {
	    cur_frm.set_query('agent_name', () => {
            return {
                query: 'service_pro.doc_events.events.get_sales_person',
            }
        })
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

cur_frm.cscript.sales_invoice = function () {
    cur_frm.doc.total_incentive = cur_frm.get_sum("sales_invoice","incentive")
    cur_frm.refresh_field("total_incentive")
}
cur_frm.cscript.incentive = function () {
   cur_frm.doc.total_incentive = cur_frm.get_sum("sales_invoice","incentive")
    cur_frm.refresh_field("total_incentive")
}
cur_frm.cscript.agent_name = function () {
    cur_frm.clear_table("sales_invoice")
    cur_frm.refresh_field("sales_invoice")
    cur_frm.call({
        doc: cur_frm.doc,
        method: 'get_sales_invoices',
        args: {},
        freeze: true,
        freeze_message: "Fetching Sales Invoices...",
        callback: (r) => {
            console.log(r.message)
            for (var i=0; i<r.message.length;i += 1){
                cur_frm.add_child("sales_invoice", r.message[i])
                cur_frm.refresh_field("sales_invoice")
                cur_frm.doc.total_incentive = cur_frm.get_sum("sales_invoice","incentive")
            cur_frm.refresh_field("total_incentive")
                    }

        }
    })

}