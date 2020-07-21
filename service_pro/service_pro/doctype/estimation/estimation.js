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
	}
});
