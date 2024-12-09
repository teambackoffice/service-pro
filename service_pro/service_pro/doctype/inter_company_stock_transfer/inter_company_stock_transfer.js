// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt
var defaults = {}
function compute_totals(cur_frm) {
    var total_qty = 0
    var debit_value = 0
    var credit_value = 0
     for(var x=0;x<cur_frm.doc.item_details.length;x+=1){
         if(cur_frm.doc.item_details[x].qty > cur_frm.doc.item_details[x].available_qty){
             cur_frm.doc.item_details[x].qty = 0
             cur_frm.refresh_field("item_details")
             frappe.throw("Qty Cannot Be More Than Available Qty")
         }
          total_qty += cur_frm.doc.item_details[x].qty
          debit_value += cur_frm.doc.item_details[x].value
          credit_value += cur_frm.doc.item_details[x].credit_value

      }
    cur_frm.doc.deference_value = debit_value - credit_value
    cur_frm.doc.total_qty = total_qty
    cur_frm.doc.debit_value = debit_value
    cur_frm.doc.credit_value = credit_value
    cur_frm.refresh_fields(["deference_value","total_qty","debit_value","credit_value"])
}
frappe.ui.form.on("Inter Company Stock Transfer Item", {
    item_code: function (frm,cdt,cdn) {
        var d = locals[cdt][cdn]
        if(d.item_code){
            cur_frm.call({
                doc: cur_frm.doc,
                method: "get_avail_qty",
                args: {
                  item: d
                },
                freeze: true,
                freeze_message: "Getting Available Qty",
                callback: function (r) {
                    d.available_qty = r.message.actual_qty
                    d.value = r.message.valuation_rate
                    cur_frm.refresh_field(d.parentfield)
                    compute_totals(cur_frm)

                }
            })

        }
        
    },
     qty: function (frm,cdt,cdn) {
       compute_totals(cur_frm)

    },
     credit_value: function (frm,cdt,cdn) {
       compute_totals(cur_frm)

    },
    item_details_remove: function () {
        compute_totals(cur_frm)
    },
})
frappe.ui.form.on("Inter Company Stock Transfer", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {
            if (frm.doc.in_transit != 1) {
                frm.add_custom_button(__('In Transit'), function () {
                    frappe.call({
                        method: "service_pro.service_pro.doctype.inter_company_stock_transfer.inter_company_stock_transfer.create_material_transfer",
                        args: {
                            name: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint(__('Material Transfer created successfully: {0}', [r.message]));
                                frm.reload_doc();
                            }
                        }
                    });
                }, __("Create"));
            }

            if (!frm.doc.is_received) {
                frm.add_custom_button(__('Received'), function () {
                    frappe.call({
                        method: "service_pro.service_pro.doctype.inter_company_stock_transfer.inter_company_stock_transfer.reserve_material_transfer",
                        args: {
                            name: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint(__('Material Issue and Receipt created successfully.'));
                                frappe.db.set_value(
                                    "Inter Company Stock Transfer",
                                    frm.doc.name,
                                    "is_received",
                                    1
                                ).then(() => {
                                    frm.reload_doc();
                                });
                            }
                        }
                    });
                }, __("Create"));
            }
        }
    },
    in_transit: function (frm) {
        frm.refresh();
    },

    auto_fill_credit_value: function () {
      for(var x=0;x<cur_frm.doc.item_details.length;x+=1){
          cur_frm.doc.item_details[x].credit_value =cur_frm.doc.item_details[x].value
          cur_frm.refresh_field("item_details")
      }
       compute_totals(cur_frm)
    },
// 	from_company: function () {
//        if(cur_frm.doc.from_company){
//             cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }
//     },
//     to_company: function () {
//        if(cur_frm.doc.to_company){
//             cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }
//     },
//     onload: function (frm) {
// 	    if(cur_frm.is_new()){
// 	       cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }

//     }
});
