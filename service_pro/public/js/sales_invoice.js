
cur_frm.cscript.incentives = function(frm){
    compute_incentives(cur_frm)
}
cur_frm.cscript.sales_team_remove = function(frm){
    compute_incentives(cur_frm)
}
cur_frm.cscript.sales_person = function(frm,cdt, cdn){
    var d = locals[cdt][cdn]
    if(d.sales_person){
        frappe.db.get_value('Sales Person', d.sales_person, "liabilities_account")
        .then(liabilities_account => {
            console.log(liabilities_account)
            cur_frm.doc.liabilities_account = liabilities_account.message.liabilities_account
        cur_frm.refresh_field("liabilities_account")
        })
    }
}
var defaults = {}
frappe.ui.form.on('Sales Invoice', {
    company: function () {
       if(cur_frm.doc.company){
            frappe.call({
                method: "service_pro.doc_events.utils.get_production_settings_defaults",
                args: {
                    company: cur_frm.doc.company
                },
                freeze: true,
                freeze_message: "Getting Company Defaults....",
                callback: function (r) {
                    defaults = r.message

                }
            })
        }
    },
   
    onload: function (frm) {
        console.log("ONLOAD")
        if(cur_frm.doc.company) {
            frappe.call({
                method: "service_pro.doc_events.utils.get_production_settings_defaults",
                args: {
                    company: cur_frm.doc.company
                },
                freeze: true,
                freeze_message: "Getting Company Defaults....",
                callback: function (r) {
                    defaults = r.message

                }
            })
        }
    },
    refresh: function(frm) {
        // frm.toggle_display("update_stock", frm.doc.is_pos)
        frappe.db.get_single_value("Production Settings", "credit_note_user_role").then((value) => {
            if(value) {
                if (!frappe.user_roles.includes(value)) {
                    frm.toggle_display("is_return", false)
                    setTimeout(() => {
                            frm.remove_custom_button('Return / Credit Note', "Create");
                    }, 500);
                }
            }                           
        });
        frm.set_query('cost_center', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        company: frm.doc.company,
                        is_group: 0,
                    }
                };
            }
        });
        frm.set_query('set_warehouse', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        company: frm.doc.company
                    }
                };
            }
        });  
    },
    is_pos: function(frm) {
        // frm.toggle_display("update_stock", frm.doc.is_pos)
        frm.doc.update_stock = 1
        if (!frm.doc.is_pos){
            frm.doc.update_stock = 0
        }
    },

    customer: function(frm){

        filter_link_field(cur_frm)
        if(cur_frm.doc.customer){
            frappe.db.get_doc("Customer", cur_frm.doc.customer)
                .then(customer => {
                    if(customer.sales_team.length > 0){
                         cur_frm.doc.sales_man = customer.sales_team[0].sales_person
                         cur_frm.doc.sales_partner = customer.sales_team[0].sales_person
                        cur_frm.refresh_fields(["sales_man","sales_partner"])
                    }

            })
        }
    },
    onload_post_render: function () {
        if(cur_frm.is_new()){
            cur_frm.doc.sales_partner = ""
            cur_frm.doc.incentive = 0
            cur_frm.doc.paid = 0
            cur_frm.doc.unpaid = 0
            cur_frm.refresh_fields(["sales_partner","incentive","paid","unpaid"])
        }
    }
})
cur_frm.cscript.paid = function(frm){
    cur_frm.doc.expense_cost_center = defaults['sales_partner_payments_details'].cost_center
    cur_frm.refresh_field("expense_cost_center")

    // cur_frm.doc.expense_account = defaults['sales_partner_payments_details'].expense_accounts
    // cur_frm.refresh_field("expense_account")

    cur_frm.doc.showroom_cash = defaults['sales_partner_payments_details'].showroom_cash
    cur_frm.refresh_field("showroom_cash")

    if(cur_frm.doc.paid){
        cur_frm.doc.unpaid = 0
        cur_frm.doc.cash = 1

        cur_frm.refresh_field("unpaid")
        cur_frm.refresh_field("cash")
    }


}
cur_frm.cscript.unpaid = function(frm){
    // frappe.db.get_single_value('Production Settings', 'expense_cost_center')
    //     .then(expense_cost_center => {
    cur_frm.doc.expense_cost_center = defaults['sales_partner_payments_details'].cost_center
    cur_frm.refresh_field("expense_cost_center")
        // })
    // frappe.db.get_single_value('Production Settings', 'expense_account')
    //         .then(expense_account => {
    //             console.log(expense_account)
    // cur_frm.doc.expense_account = defaults['sales_partner_payments_details'].expense_accounts
    // cur_frm.refresh_field("expense_account")
    cur_frm.doc.liabilities_account = defaults['sales_partner_payments_details'].expense_accounts
    cur_frm.refresh_field("liabilities_account")
        // })
   if(cur_frm.doc.unpaid){
        cur_frm.doc.paid = 0
        cur_frm.doc.cash = 0
        cur_frm.refresh_field("paid")
        cur_frm.refresh_field("cash")
   }


}
cur_frm.cscript.onload = function(frm){
    if(cur_frm.doc.docstatus === 0 && cur_frm.doc.production.length > 0 && cur_frm.doc.taxes_and_charges){
        cur_frm.trigger("taxes_and_charges")
        cur_frm.save()
    }
    if(cur_frm.is_new() && cur_frm.doc.is_return){
        for(var i =0; i < cur_frm.doc.production.length;i+=1){
            cur_frm.doc.production[i].qty = 0 - cur_frm.doc.production[i].qty
            cur_frm.refresh_field("production")
        }
    }
    filter_link_field(cur_frm)

    cur_frm.set_query('expense_cost_center', () => {
        return {
            filters: {
                is_group: 0,
            }
        }
    });
    if('sales_partner_payments_details' in defaults){
        // cur_frm.doc.expense_account = defaults['sales_partner_payments_details'].expense_account
        // cur_frm.refresh_field("expense_account")

        cur_frm.doc.showroom_cash = defaults['sales_partner_payments_details'].showroom_cash
        cur_frm.refresh_field("showroom_cash")

        // cur_frm.doc.showroom_card = defaults['incentive_journal_defaults'].showroom_card
        // cur_frm.refresh_field("showroom_card")
    }
    if('sales_partner_payments_details' in defaults){

        cur_frm.doc.showroom_cash = defaults['sales_partner_payments_details'].showroom_cash
        cur_frm.refresh_field("showroom_cash")
    }


}
function compute_incentives(cur_frm) {
    var incentive_total = 0
    for(var i=0;i<cur_frm.doc.sales_team.length;i+=1){
        incentive_total += cur_frm.doc.sales_team[i].incentives
    }
    cur_frm.doc.incentive = incentive_total
    cur_frm.refresh_field("incentive")
}
function filter_link_field(cur_frm) {
     cur_frm.set_query('reference', 'production', () => {
        return {
            filters: [
                ["customer", "=", cur_frm.doc.customer],
                ["docstatus", "=", 1],
                ["status", "in", ["To Deliver and Bill", "To Bill","Partially Completed", "Partially Delivered"]],
            ]
        }
    })

}

cur_frm.cscript.reference = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
    if(d.reference){
         frappe.db.get_doc('Production', d.reference)
            .then(doc => {
                var add = true
                var qty_1 = doc.qty
                for(var x=0;x < cur_frm.doc.items.length;x += 1){
                    if(cur_frm.doc.items[x].item_code === doc.item_code_prod){
                        add = false
                    }
                }
                frappe.call({
                    method: "service_pro.service_pro.doctype.production.production.get_dn_si_qty",
                    args: {
                        item_code: doc.item_code_prod,
                        qty:   doc.qty,
                        name: d.reference
                    },
                    async: false,
                    callback: function (r) {
                        qty_1 = r.message

                    }
                })
                d.qty = qty_1
                d.rate = doc.invoice_rate
                d.amount =doc.invoice_rate *qty_1
                cur_frm.refresh_field("production")

        if(add){
        // frappe.db.get_single_value('Production Settings', 'income_account')
            // .then(income_account => {
                frappe.db.get_doc('Item', doc.item_code_prod)
                    .then(doc1 => {
                         cur_frm.add_child('items', {
                            item_code: doc.item_code_prod,
                            qty: qty_1,
                            uom: doc.umo,
                            stock_uom: doc.umo,
                            rate: doc.invoice_rate,
                            amount: doc.invoice_rate * qty_1,
                            item_name: doc1.item_name,
                            description: doc1.description,
                            income_account: defaults['finish_good_defaults'].income_account,

                        });

                    cur_frm.refresh_field('items');
                })
            // })

            if(doc.sales_man){
                cur_frm.add_child('sales_man', {
                    sales_man: doc.sales_man,
                    reference: d.reference,
                });
                cur_frm.refresh_field('sales_man');

            }



        }

            })
    }
}
