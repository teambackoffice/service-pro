frappe.ui.form.on("Material Request", {
    refresh: function (frm) {
        frm.set_query('set_warehouse', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        company: frm.doc.company,
                        is_group: 0,
                    }
                };
            }
        });
        // Remove existing buttons under "Create"
        ["Purchase Order", "Request for Quotation", "Supplier Quotation"].forEach(button => {
            frm.remove_custom_button(button, "Create");
        });

        // Only add the custom button after submission (docstatus === 1)
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
                __('Purchase Order'),
                function () {
                   

                    frappe.model.open_mapped_doc({
                        method: "service_pro.doc_events.material_request.make_purchase_order",
                        frm: frm,
                        args: {
                            supplier: frm.doc.internal_supplier
                        },
                        freeze: true,
                    });
                },
                __("Create")
            );
        }
    }
});




cur_frm.cscript.customer = function(frm){
    filter_link_field(cur_frm)

}
cur_frm.cscript.onload = function(frm){
    filter_link_field(cur_frm)

}

function filter_link_field(cur_frm) {
     cur_frm.set_query('reference', 'production', () => {
        return {
            filters: [
                ["docstatus", "=", 1],
                ["status", "in", ["To Deliver and Bill", "In Progress"]],
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

            })
    }
}