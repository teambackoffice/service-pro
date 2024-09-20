// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

let doc = ["Lead", "Customer"];
frappe.ui.form.on("Service Order Form", {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status != "Expired") {
            frm.add_custom_button(__('Sales Order'), function() {
                frappe.model.open_mapped_doc({
                    method: "service_pro.service_pro.doctype.service_order_form.service_order_form.create_sales_order",
                    frm: frm,
                    run_link_triggers: true
                });
            },__('Create'));
        }
        calculate_total(frm);

        frm.set_query('sof_to', function() {
            return {
                filters: {
                    name: ["in" ,doc] 
                }
            };
        });



    },
    vat_on: function(frm) {
        if (frm.doc.vat_on) {
            frappe.db.get_value('Sales Taxes and Charges Template', frm.doc.vat_on, 'custom_tax_rate', (r) => {
                if (r && r.custom_tax_rate) {
                    frm.set_value('tax_amount', r.custom_tax_rate);
                }
            });
        }
        
    },
    currency: function(frm){
        var company_currency = erpnext.get_currency(frm.doc.company)
        frm.set_currency_labels(["rate", "amount"], frm.doc.currency, "option1");
        if(frm.doc.currency && frm.doc.currency !== company_currency
            && !frm.doc.__onload?.load_after_mapping) {
                frappe.call({
                    method: "erpnext.setup.utils.get_exchange_rate",
                    args: {
                        transaction_date: frm.doc.posting_date,
                        from_currency: frm.doc.currency,
                        to_currency: company_currency,
                        args: "for_selling"
                    },
                    freeze: true,
                    freeze_message: __("Fetching exchange rates ..."),
                    callback: function(r) {
                        if(flt(r.message) != frm.doc.conversion_rate) {
                            // me.set_margin_amount_based_on_currency(exchange_rate);
                            // me.set_actual_charges_based_on_currency(exchange_rate);
                            frm.set_value("conversion_rate", flt(r.message));
                            $.each(frm.doc.option1 || [], function(i, d) {
                                frappe.model.set_value(d.doctype, d.name, "rate",
                                    flt(d.rate) / flt(r.message));
                                frappe.model.set_value(d.doctype, d.name, "amount",
                                    flt(d.rate) / flt(r.message));
                            });
                        }
                    }
                });
        // frm.get_exchange_rate(transaction_date, frm.doc.currency, company_currency,
        //     function(exchange_rate) {
        //         if(exchange_rate != frm.doc.conversion_rate) {
        //             // me.set_margin_amount_based_on_currency(exchange_rate);
        //             // me.set_actual_charges_based_on_currency(exchange_rate);
        //             frm.set_value("conversion_rate", exchange_rate);
        //         }
        //     });
        } else {
            // company currency and doc currency is same
            // this will prevent unnecessary conversion rate triggers
            if(frm.doc.currency === company_currency) {
                frm.set_value("conversion_rate", 1.0);
            }else{
                const subs =  [conversion_rate_label, frm.doc.currency, company_currency];
                const err_message = __('{0} is mandatory. Maybe Currency Exchange record is not created for {1} to {2}', subs);
                frappe.throw(err_message);
            }
        }
            // frm.doc.conversion_rate = flt(frm.doc.conversion_rate, (cur_frm) ? precision("conversion_rate") : 9);
            // var conversion_rate_label = frappe.meta.get_label(frm.doc.doctype, "conversion_rate",
            //     frm.doc.name);
            // var company_currency = erpnext.get_currency(frm.doc.company)
    
            // if(!frm.doc.conversion_rate) {
            //     if(frm.doc.currency == company_currency) {
            //         frm.set_value("conversion_rate", 1);
            //     } else {
            //         const subs =  [conversion_rate_label, frm.doc.currency, company_currency];
            //         const err_message = __('{0} is mandatory. Maybe Currency Exchange record is not created for {1} to {2}', subs);
            //         frappe.throw(err_message);
            //     }
            // }
    },
    get_company_currency() {
        return erpnext.get_currency(frm.doc.company);
    },
    get_exchange_rate(transaction_date, from_currency, to_currency, callback) {
		var args  = "for_selling";

		if (!transaction_date || !from_currency || !to_currency) return;
		return frappe.call({
			method: "erpnext.setup.utils.get_exchange_rate",
			args: {
				transaction_date: transaction_date,
				from_currency: from_currency,
				to_currency: to_currency,
				args: args
			},
			freeze: true,
			freeze_message: __("Fetching exchange rates ..."),
			callback: function(r) {
                console.log(r.message)
				callback(flt(r.message));
			}
		});
	},
    option1_add: function(frm, cdt, cdn) {
        calculate_total(frm);
        
    },

    option1_remove: function(frm, cdt, cdn) {
        calculate_total(frm);
       
    },

    additional_discount_percentage: function(frm) {
        calculate_total(frm);
       
    },
    additional_discount_amount: function(frm) {
        calculate_total(frm);
    },

    apply_additional_discount_on: function(frm) {
        calculate_total(frm);
    },
    

    tax_amount: function(frm) {
        calculate_total(frm);
    },

    
});

frappe.ui.form.on('Service Order Form Item', {
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    discount: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    discount_percentage: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];  

    let qty = row.qty || 0;
    let rate = row.rate || 0;
    let discount = row.discount || 0;
    let discount_percentage = row.discount_percentage || 0;

    let amount = qty * rate;

    if (discount_percentage > 0) {
        let discountAmountPercentage = (amount * discount_percentage) / 100;
        
        frappe.model.set_value(cdt, cdn, 'discount', discountAmountPercentage);
        
        amount -= discountAmountPercentage;
    } else {
        amount -= discount;
    }

    amount = Math.max(amount, 0);

    frappe.model.set_value(cdt, cdn, 'amount', amount);

    frm.refresh_field('option1'); 
}


function calculate_total(frm) {
    let total = 0;
    let total_qty = 0; 

    frm.doc.option1.forEach(function(row) {
        total += row.amount || 0;
        total_qty += row.qty || 0; 
    });

    frm.set_value('total', total);
    frm.set_value('total_quantity', total_qty); 

    let additional_discount_percentage = frm.doc.additional_discount_percentage || 0;
    let additional_discount_amount = frm.doc.additional_discount_amount || 0;
    let net_total = total;
    let grand_total = total;

    if (frm.doc.apply_additional_discount_on === 'Net Total') {
        if (additional_discount_percentage > 0) {
            additional_discount_amount = (total * additional_discount_percentage) / 100;
            net_total -= additional_discount_amount;
        } else if (additional_discount_amount > 0) {
            net_total -= additional_discount_amount;
        }

        net_total = Math.max(net_total, 0);

        frm.set_value('net_total', net_total);
        grand_total = net_total;
    } else if (frm.doc.apply_additional_discount_on === 'Grand Total') {
        if (additional_discount_percentage > 0) {
            additional_discount_amount = (total * additional_discount_percentage) / 100;
            grand_total -= additional_discount_amount;
        } else if (additional_discount_amount > 0) {
            grand_total -= additional_discount_amount;
        }

        grand_total = Math.max(grand_total, 0);

        frm.set_value('net_total', total);
    }

    frm.set_value('additional_discount_amount', additional_discount_amount);

    let tax_amount = frm.doc.tax_amount || 0;
    grand_total += tax_amount;

    grand_total = Math.max(grand_total, 0);

    frm.set_value('grand_total', grand_total);
}
