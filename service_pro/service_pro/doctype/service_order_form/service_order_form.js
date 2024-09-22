// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

let doc = ["Lead", "Customer"];
frappe.ui.form.on("Service Order Form", {
    onload: function(frm) {
        if (!frm.doc.vat_on && frm.is_new()) {
            frappe.db.get_value('Production Settings', {name: 'Production Settings'}, 'service_order_form_default_tax', (r) => {
                if (r && r.service_order_form_default_tax) {
                    frm.set_value('vat_on', r.service_order_form_default_tax);
                }
            });
        }

        frm.refresh_field('vat_on');
        frm.trigger('vat_on');
    },
    refresh: function(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status != "Expired") {
            frm.add_custom_button(__('Sales Order'), function() {
                frappe.model.open_mapped_doc({
                    method: "service_pro.service_pro.doctype.service_order_form.service_order_form.create_sales_order",
                    frm: frm,
                    run_link_triggers: true
                });
            }, __('Create'));
        }
    
        frm.set_query('sof_to', function() {
            return {
                filters: {
                    name: ["in", doc] 
                }
            };
        });
    
    },
    vat_on: function(frm) {
        tax_rate(frm)
    },
    net_total: function(frm) {
        tax_rate(frm)
    },
    additional_discount_amount: function(frm) {
        calculate_total(frm);
    },
    additional_discount_percentage: function(frm) {
        calculate_discount(frm);
    },
    apply_additional_discount_on: function(frm) {
        calculate_total(frm);
        
    },
    validate:function(frm){
        if(!frm.doc.vat_on){
            frm.set_value("tax_amount",0)
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
                    callback: function(r) {
                        if(r.message) {
                            $.each(frm.doc.option1 || [], function(i, d) {
                                frappe.model.set_value(d.doctype, d.name, "rate",
                                    flt(d.rate) / flt(r.message));
                                frappe.model.set_value(d.doctype, d.name, "amount",
                                    flt(d.rate) / flt(r.message));
                            });
                        }
                    }
                });
        } else {
            
        }
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
});

frappe.ui.form.on('Service Order Form Item', {
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    let total = 0;
    let total_qty = 0;
    let total_disc = 0;

    frm.doc.option1.forEach(function(row) {
        total += row.amount || 0;
        total_qty += row.qty || 0;
        total_disc += row.discount || 0; 

    });

    frm.set_value('total', total);
    frm.set_value('net_total', total);
    frm.set_value('total_quantity', total_qty);
    frm.set_value('additional_discount_amount', total_disc); 
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        let total = 0;
        let total_qty = 0;
        let total_disc = 0;
    
        frm.doc.option1.forEach(function(row) {
            total += row.amount || 0;
            total_qty += row.qty || 0;
            total_disc += row.discount || 0; 
    
        });
    
        frm.set_value('total', total);
        frm.set_value('net_total', total);
        frm.set_value('total_quantity', total_qty);
        frm.set_value('additional_discount_amount', total_disc);
        calculate_total(frm)
    },
    discount: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        let total = 0;
        let total_qty = 0;
        let total_disc = 0;
    
        frm.doc.option1.forEach(function(row) {
            total += row.amount || 0;
            total_qty += row.qty || 0;
            total_disc += row.discount || 0; 
    
        });
    
        frm.set_value('total', total);
        frm.set_value('net_total', total);
        frm.set_value('total_quantity', total_qty);
        frm.set_value('additional_discount_amount', total_disc);
        calculate_total(frm)
    },
    discount_percentage: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        
        let total = 0;
        let total_qty = 0;
        let total_disc = 0;
    
        frm.doc.option1.forEach(function(row) {
            total += row.amount || 0;
            total_qty += row.qty || 0;
            total_disc += row.discount || 0; 
    
        });
    
        frm.set_value('total', total);
        frm.set_value('net_total', total);
        frm.set_value('total_quantity', total_qty);
        frm.set_value('additional_discount_amount', total_disc);
        calculate_total(frm)
    }
});

function tax_rate(frm) {
    if (frm.doc.vat_on) {
        frappe.db.get_value('Sales Taxes and Charges Template', frm.doc.vat_on, 'custom_tax_rate', (r) => {
            if (r && r.custom_tax_rate) {
                let tax_rate = r.custom_tax_rate / 100;
                let net_total = frm.doc.net_total || 0;
                let tax_amount = net_total * tax_rate;
                frm.set_value('tax_amount', tax_amount);
                frm.set_value('grand_total', frm.doc.net_total+tax_amount)
            }
        });
    }
}

function calculate_total(frm) {
    let discount_percentage = frm.doc.additional_discount_percentage || 0
    let additional_discount_amount = frm.doc.additional_discount_amount || 0
    var net_total = 0
    let grand_total = 0
    frm.doc.option1.forEach(function(row) {
        net_total+=row.amount || 0;
    })
    if (frm.doc.apply_additional_discount_on === 'Net Total') {
        var distributed_amount = flt(additional_discount_amount)*net_total/net_total
        var net_amount = flt(net_total - distributed_amount)
        frm.set_value("net_total",net_amount)
    }else{
        frappe.db.get_value('Sales Taxes and Charges Template', frm.doc.vat_on, 'custom_tax_rate', (r) => {
            if (r && r.custom_tax_rate) {
                let tax_rate = r.custom_tax_rate / 100;
                let tax_amount = net_total * tax_rate;
                grand_total = net_total+tax_amount
            }
            var distributed_amount = flt(additional_discount_amount)*net_total/grand_total
            var net_amount = flt(net_total - distributed_amount)
            frm.set_value("net_total",net_amount)
        });
    }
}

function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];  

    let qty = row.qty || 0;
    let rate = row.rate || 0;

   
    let discount_percentage = row.discount_percentage || 0;

    let amount = qty * rate;

    if (discount_percentage > 0) {
        let discountAmountPercentage = (amount * discount_percentage) / 100;
        
        frappe.model.set_value(cdt, cdn, 'discount', discountAmountPercentage);
        
        amount -= discountAmountPercentage;
    } 

    amount = Math.max(amount, 0);

    frappe.model.set_value(cdt, cdn, 'amount', amount);

    frm.refresh_field('option1'); 
}

function calculate_discount(frm) {
    let net_total =  0;
    frm.doc.option1.forEach(function(row) {
        net_total+=row.amount || 0;
    })
    let additional_discount_percentage = frm.doc.additional_discount_percentage || 0;

    let additional_discount_amount = (net_total * additional_discount_percentage) / 100;
    frm.set_value('additional_discount_amount', additional_discount_amount);
}