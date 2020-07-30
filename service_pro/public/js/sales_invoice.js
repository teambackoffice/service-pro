
cur_frm.cscript.customer = function(frm){
    filter_link_field(cur_frm)

}
cur_frm.cscript.onload = function(frm){
    filter_link_field(cur_frm)

}

function filter_link_field(cur_frm) {
     cur_frm.set_query('reference', 'production', () => {
        return {
            filters: {
                customer: cur_frm.doc.customer,
                docstatus: 1,
                status: "In Progress"
            }
        }
    })
}

cur_frm.cscript.reference = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
    if(d.reference){
         frappe.db.get_doc('Production', d.reference)
            .then(doc => {
                d.qty = doc.qty
                d.rate = doc.rate
                d.amount = doc.amount
                cur_frm.refresh_field("production")
                frappe.db.get_doc('Item', doc.item_code_prod)
                    .then(doc1 => {
                         cur_frm.add_child('items', {
                            item_code: doc.item_code_prod,
                            qty: doc.qty,
                            uom: doc.umo,
                            rate: doc.rate,
                            amount: doc.amount,
                            item_name: doc1.item_name,
                            income_account: doc.income_account,
                            description: doc1.description,
                        });

                    cur_frm.refresh_field('items');
                })
            })
    }
}