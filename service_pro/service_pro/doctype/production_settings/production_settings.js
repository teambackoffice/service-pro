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
        cur_frm.set_query('raw_material_cost_center', () => {
        return {
            filters: {
                is_group: 0,
            }
        }
        })
        cur_frm.set_query('finish_good_cost_center', () => {
        return {
            filters: {
                is_group: 0,
            }
        }
        })
	}
});
