// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Partner Payments", {
    company: function () {
        cur_frm.call({
            doc: cur_frm.doc,
            method: "get_defaults",
            freeze: true,
            freeze_message: "Getting Default....",
            calback: function () {
            }
        })
    },
    refresh: function () {
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
    },
	onload_post_render: function(frm) {
        if(cur_frm.is_new()){
            cur_frm.doc.status = "Unpaid"
            cur_frm.doc.paid_amount = 0
            cur_frm.doc.balance_amount = cur_frm.doc.incentive
            cur_frm.refresh_fields(["status","paid_amount","balance_amount"])
        }
	},
});
