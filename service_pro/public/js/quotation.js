
cur_frm.cscript.onload = function () {
    if(cur_frm.is_new()){
        for(var x=0;x<cur_frm.doc.items.length;x += 1){
            var item = cur_frm.doc.items[x]
            console.log(item.item_code)
            frappe.call({
                method: "service_pro.doc_events.quotation.get_rate",
                args:{
                    item_code: item.item_code
                },
                callback: function (r) {
                    item.rate = r.message[0]
                    item.amount = r.message[0] * item.qty
                    cur_frm.refresh_field("items")
                }
            })
        }

    }
}