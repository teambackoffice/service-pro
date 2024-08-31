// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Partner Payments", {
	onload_post_render: function(frm) {
        if(cur_frm.is_new()){
            cur_frm.doc.status = "Unpaid"
            cur_frm.doc.paid_amount = 0
            cur_frm.doc.balance_amount = cur_frm.doc.incentive
            cur_frm.refresh_fields(["status","paid_amount","balance_amount"])
        }
	},
});
