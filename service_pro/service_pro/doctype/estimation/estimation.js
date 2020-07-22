// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Estimation', {
	onload: function(frm) {
        frappe.call({
            method: "service_pro.service_pro.doctype.estimation.estimation.get_dimensions",
            args:{},
            callback: function (r) {
                frm.set_df_property('rod_dia', 'options', r.message[0])
                frm.set_df_property('r_length', 'options', r.message[1])
                frm.set_df_property('tube_size', 'options', r.message[2])
                frm.set_df_property('t_length', 'options', r.message[3])
            }
        })
	},
    // refresh: function () {
	 //    frappe.db.get_list('Production', {
    //             fields: ["*"],
    //             filters: {
    //                 receipt_note: cur_frm.docname,
    //                 docstatus: 0
    //             }
    //         }).then(records => {
    //             if(records.length > 0){
    //
    //                 frm.add_custom_button(__("Submit Estimation/s"), () => {
    //                     submit_estimations(frm, cur_frm)
    //
    //                 }, __("Submit"))
    //             }
    //         })
    //
    // }
});
 // function create_quotation(frm, cur_frm) {
 //
 //            frappe.model.open_mapped_doc({
 //                method: "service_pro.service_pro.doctype.estimation.estimation.make_production",
 //                frm: me.frm
 //            })
 //        }