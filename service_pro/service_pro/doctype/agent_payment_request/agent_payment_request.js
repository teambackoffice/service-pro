// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Agent Payment Request Table', {
    sales_invoice_remove: function () {
      cur_frm.doc.total_incentive = cur_frm.get_sum("sales_invoice","incentive")
                cur_frm.refresh_field("total_incentive")
    },
})
frappe.ui.form.on('Agent Payment Request', {
    company: function () {
      cur_frm.trigger("agent_name")
    },
	claim_amount: function(frm) {
	    cur_frm.doc.agent_outstanding_amount = cur_frm.doc.claim_amount
        cur_frm.refresh_field("agent_outstanding_amount")
    },
	refresh: function(frm) {
	    if(cur_frm.doc.docstatus){
	         cur_frm.add_custom_button(__('Accounting Ledger'), function() {
                frappe.route_options = {
                    voucher_no: cur_frm.doc.name,
                    from_date: cur_frm.doc.posting_date,
                    to_date: moment(cur_frm.doc.modified).format('YYYY-MM-DD'),
                    company:cur_frm.doc.company,
                    group_by: "Group by Voucher (Consolidated)",
                    show_cancelled_entries: cur_frm.doc.docstatus === 2,
                    ignore_prepared_report: true
                };
                frappe.set_route("query-report", "General Ledger");
            }, __("View"));
        }


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
        // if(cur_frm.doc.docstatus && !show){
	     //     frm.add_custom_button(__("Journal Entry"), () => {
        //             cur_frm.call({
        //                 doc: cur_frm.doc,
        //                 method: 'generate_journal_entry',
        //                 args: {},
        //                 freeze: true,
        //                 freeze_message: "Generating Journal Entry...",
        //                 callback: (r) => {
        //                     cur_frm.reload_doc()
        //                         frappe.set_route("Form", "Journal Entry", r.message);
        //                 }
        //         })
        //     }, "Generate")
        // }

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