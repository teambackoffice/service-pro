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


         cur_frm.set_query('income_account',"finish_good_defaults", (frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    account_type: "Income Account",
                    company: d.company,
                    disabled: 0,
                  is_group: 0,
                }
            }
        })
        cur_frm.set_query('finish_good_warehouse',"finish_good_defaults", (frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    company: d.company,
                    disabled: 0,
                      is_group: 0,
                }
            }
        })
        cur_frm.set_query('finish_good_cost_center',"finish_good_defaults", (frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('cost_center',"raw_material_defaults", (frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('warehouse',"raw_material_defaults", (frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })

        cur_frm.set_query('cost_center',"site_job_report_settings" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('warehouse',"site_job_report_settings" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('expense_account',"incentive_journal_defaults" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('expense_cost_center',"incentive_journal_defaults" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('expense_accounts',"sales_partner_payments_details" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('payable_account',"sales_partner_payments_details" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('cost_center',"sales_partner_payments_details" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })

        cur_frm.set_query('account',"from_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('warehouse',"from_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('cost_center',"from_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('account',"to_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('warehouse',"to_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
        cur_frm.set_query('cost_center',"to_companies" ,(frm,cdt,cdn) => {
            var d = locals[cdt][cdn]
            return {
                filters: {
                    is_group: 0,
                    company: d.company,
                    disabled: 0
                }
            }
        })
	},


});
