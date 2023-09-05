frappe.ui.form.on('Landed Cost Voucher', {
    refresh_avail_qty:function(frm){
        frappe.call({
            method:"service_pro.doc_events.landed_cost_voucher.get_item_avail_qty",
            args:{items:frm.doc.items},
            callback:function(r){
                r.message.forEach(row=>{
                    if(row.item_code){
                        frm.doc.items.forEach(i=>{
                            if(i.item_code == row.item_code){
                                i.avail_qty = row.avail_qty 
                            }
                        });
                        frm.refresh_field("items");
                        frm.dirty();
                    }
                })
            }
        })
        
    },
    before_submit:function(frm){
        frm.doc.items.forEach(i=>{
            if(i.avail_qty == 0){
                frappe.throw(`Item <b>${i.item_code}</b> is not available!`);
            }
        })
    }
});