// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Settings', {
	refresh: function(frm) {
	     cur_frm.call({
              doc: cur_frm.doc,
              method: "get_series",
              freeze: true,
              freeze_message: "Generating Item....",
              callback: function(r){
                  cur_frm.set_df_property("item_naming_series","options",r.message)
                  // cur_frm.doc.item_code_prod = r.message
                  // cur_frm.refresh_field("item_code_prod")
              }
          })
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
        cur_frm.set_query('expense_cost_center', () => {
        return {
            filters: {
                is_group: 0,
            }
        }
        })
	},


});
