// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Settings', {
	refresh: function(frm) {
         cur_frm.set_query('income_account', () => {
        return {
            filters: {
                account_type: "Income Account",
            }
        }
    })
	}
});
