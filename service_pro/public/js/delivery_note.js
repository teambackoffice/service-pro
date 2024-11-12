frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
    frm.set_query('cost_center', function() {
        if (frm.doc.company) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        }
    });
}
});

cur_frm.cscript.customer = function(frm){
    filter_link_field(cur_frm)

}
cur_frm.cscript.onload = function(frm){
    filter_link_field(cur_frm)
    if(cur_frm.is_new() && cur_frm.doc.is_return){
        for(var i =0; i < cur_frm.doc.production.length;i+=1){
            cur_frm.doc.production[i].qty = 0 - cur_frm.doc.production[i].qty
            cur_frm.refresh_field("production")
        }
    }
}

function filter_link_field(cur_frm) {
      cur_frm.fields_dict.production.grid.get_field("reference").get_query =
			function() {
				return {
				    filters: [
                        ["customer", "=", cur_frm.doc.customer],
                        ["docstatus", "=", 1],
                        ["status", "in", ["To Bill", "To Deliver and Bill", "To Deliver","Partially Completed", "Partially Delivered"]]
                    ]
                }
            }

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
                        qty: doc.qty,
                        name: d.reference
                    },
                    async: false,
                    callback: function (r) {
                        qty_1 = r.message

                    }
                })
                d.qty = qty_1
                d.rate = doc.rate
                d.amount = doc.amount
                cur_frm.refresh_field("production")

        if(add){
             frappe.db.get_doc('Item', doc.item_code_prod)
                    .then(doc1 => {
                         cur_frm.add_child('items', {
                            item_code: doc.item_code_prod,
                            qty: qty_1,
                            uom: doc.umo,
                            stock_uom: doc.umo,
                            rate: doc.rate,
                            amount: doc.amount,
                            item_name: doc1.item_name,
                            description: doc1.description,
                        });

                    cur_frm.refresh_field('items');
                })

        }

            })
    }
}