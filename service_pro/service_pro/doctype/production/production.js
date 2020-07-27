// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt
cur_frm.cscript.qty_raw_material = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
    if(d.qty_raw_material && d.qty_raw_material <= d.available_qty){
        d.amount_raw_material = d.rate_raw_material * d.qty_raw_material
        cur_frm.refresh_field("raw_material")
    } else {
        var qty = d.qty_raw_material
        d.qty_raw_material = d.available_qty
        d.amount_raw_material = d.rate_raw_material * d.available_qty
        cur_frm.refresh_field("raw_material")
        frappe.throw("Not enough stock. Can't change to " + qty.toString())

    }
    compute_raw_material_total(cur_frm)
}
cur_frm.cscript.rate_raw_material = function (frm,cdt,cdn) {
   var d = locals[cdt][cdn]
    if(d.rate_raw_material){
        d.amount_raw_material = d.rate_raw_material * d.qty_raw_material
        cur_frm.refresh_field("raw_material")
    }
    compute_raw_material_total(cur_frm)
}
cur_frm.cscript.raw_material_add = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
   frappe.db.get_single_value('Production Settings', 'raw_material_warehouse')
        .then(warehouse => {
            d.warehouse = warehouse
            cur_frm.refresh_field("raw_material")
        })
    frappe.db.get_single_value('Production Settings', 'raw_material_cost_center')
        .then(cost_center => {
            d.cost_center = cost_center
            cur_frm.refresh_field("raw_material")
        })
}
cur_frm.cscript.raw_material_remove = function (frm,cdt,cdn) {
    compute_raw_material_total(cur_frm)
}
cur_frm.cscript.cost = function (frm,cdt,cdn) {
    compute_scoop_of_work_total(cur_frm)
}
cur_frm.cscript.scoop_of_work_remove = function (frm,cdt,cdn) {
    compute_scoop_of_work_total(cur_frm)
}
function compute_scoop_of_work_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.scoop_of_work.length;x += 1){
        total += cur_frm.doc.scoop_of_work[x].cost
    }
    cur_frm.doc.scoop_of_work_total = total
    cur_frm.refresh_field("scoop_of_work_total")
}
function compute_raw_material_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.raw_material.length;x += 1){
        total += cur_frm.doc.raw_material[x].amount_raw_material
    }
    cur_frm.doc.raw_material_total = total
    cur_frm.refresh_field("raw_material_total")
}
frappe.ui.form.on('Production', {
    onload: function () {
        if(cur_frm.is_new()){
             frappe.db.get_single_value('Production Settings', 'finish_good_warehouse')
            .then(warehouse => {
                cur_frm.doc.warehouse = warehouse
                cur_frm.refresh_field("warehouse")
            })
            frappe.db.get_single_value('Production Settings', 'finish_good_cost_center')
            .then(cost_center => {
                cur_frm.doc.cost_center = cost_center
                cur_frm.refresh_field("cost_center")
            })
            frappe.db.get_single_value('Production Settings', 'income_account')
            .then(income_account => {
                cur_frm.doc.income_account = income_account
                cur_frm.refresh_field("income_account")
            })
        }

        var status = frappe.meta.get_docfield("Scoop of Work", "status", cur_frm.doc.name);
        status.read_only = (cur_frm.doc.status === "Completed")
        frm.set_df_property('rate', 'read_only', cur_frm.doc.status === "Completed");
        frm.set_df_property('qty', 'read_only', cur_frm.doc.status === "Completed");

    },
    validate: function (frm) {
        frm.set_df_property('type', 'read_only', 1);

    },
	refresh: function() {
	    cur_frm.set_query('income_account', () => {
            return {
                filters: {
                    is_group: 0,
                }
            }
        })
        var generate_button = true

        for(var x=0;x<cur_frm.doc.scoop_of_work.length;x += 1){
            if(cur_frm.doc.scoop_of_work[x].status === "In Progress"){
                generate_button = false
            }
        }

        if(generate_button && cur_frm.doc.status === "In Progress"){
            cur_frm.add_custom_button(__("Generate Sales Invoice"), () => {
                 cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'generate_si',
                    freeze: true,
                    freeze_message: "Generating Sales Invoice ...",
                    callback: () => {}
                })
            });
        }
	},
    customer: function() {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
        }
        if(cur_frm.doc.customer){
	        console.log("HAHA")
	         frappe.db.get_doc("Customer", cur_frm.doc.customer)
            .then(doc => {
                console.log("NAA MAN")
                cur_frm.doc.customer_name = doc.customer_name
                cur_frm.refresh_field("customer_name")
            })

            frappe.call({
                method: "service_pro.service_pro.doctype.production.production.get_address",
                args:{
                    customer: cur_frm.doc.customer
                },
                callback: function (r) {
                    if(r.message){
                        cur_frm.doc.address = r.message.name
                        cur_frm.doc.address_name = r.message.address_line1 + "\n" +
                            r.message.city + "\n" +
                            r.message.county + "\n" +
                            r.message.country + "\n" +
                            r.message.state + "\n" +
                            r.message.pincode
                        cur_frm.refresh_field("address")
                        cur_frm.refresh_field("address_name")
                    }

                }
            })
        }
	},
    type: function(frm) {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
//             SK-
// SK-D-
// HA-
            frm.set_df_property('series', 'options', ['HA-'])
            cur_frm.doc.series = "HA-"
            cur_frm.refresh_field("series")
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Assemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');

	        frm.set_df_property('series', 'options', ['','SK-','HA-'])
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Disassemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');

	        frm.set_df_property('series', 'options', ['SK-D-'])
            cur_frm.doc.series = "SK-D-"
            cur_frm.refresh_field("series")
        }
	},
    estimation: function(frm) {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service" && cur_frm.doc.estimation){
            get_items_from_estimation(frm,cur_frm)

        } else {
            cur_frm.doc.item_code_prod = undefined
            cur_frm.doc.qty = 0
            cur_frm.doc.rate = 0
            cur_frm.doc.amount = 0
            cur_frm.refresh_field("item_code")
            cur_frm.refresh_field("qty")
            cur_frm.refresh_field("rate")
            cur_frm.refresh_field("amount")

        }
	},
    address: function(frm) {
         frappe.db.get_doc("Address", cur_frm.doc.address)
            .then(doc => {
                cur_frm.doc.address_name =  cur_frm.doc.address_name = r.message.address_line1 + "\n" +
                            r.message.city + "\n" +
                            r.message.county + "\n" +
                            r.message.country + "\n" +
                            r.message.state + "\n" +
                            r.message.pincode
             cur_frm.refresh_field("address_name")
            })
	},

});

function filter_link_field(cur_frm) {
     cur_frm.set_query('estimation', () => {
        return {
            filters: {
                customer: cur_frm.doc.customer,
                docstatus: 1,
            }
        }
    })
}
function get_items_from_estimation(frm,cur_frm) {
   frappe.db.get_doc('Estimation', cur_frm.doc.estimation)
    .then(doc => {
        set_scoop_of_work(doc,frm)
        set_raw_material(doc,frm)
        cur_frm.doc.item_code_prod = doc.item_code
        cur_frm.doc.qty = doc.qty
        cur_frm.doc.rate = doc.rate
        cur_frm.doc.amount = doc.qty * doc.rate
        cur_frm.refresh_field("item_code")
        cur_frm.refresh_field("qty")
        cur_frm.refresh_field("rate")
        cur_frm.refresh_field("amount")

    })
}
function set_scoop_of_work(doc, frm) {
    cur_frm.clear_table("scoop_of_work")
  for(var i =0;i<doc.scoop_of_work.length;i+=1){
      var row = doc.scoop_of_work[i]
      frm.add_child('scoop_of_work', {
            work_name: row.work_name,
            estimated_date: row.estimated_date,
            cost: row.cost,
        });

    frm.refresh_field('scoop_of_work');
      compute_scoop_of_work_total(cur_frm)

  }
}
function set_raw_material(doc, frm) {
    cur_frm.clear_table("raw_material")
  for(var i =0;i<doc.raw_material.length;i+=1){
      var row = doc.raw_material[i]
      frm.add_child('raw_material', {
            item_code: row.item_code,
            warehouse: row.warehouse,
            available_qty: row.available_qty,
            qty_raw_material: row.qty_raw_material,
            rate_raw_material: row.rate_raw_material,
            amount_raw_material: row.amount_raw_material
        });

    frm.refresh_field('raw_material');
    compute_raw_material_total(cur_frm)
  }
}

cur_frm.cscript.warehouse = function (frm,cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.item_code && d.warehouse){
        frappe.call({
            method: "service_pro.service_pro.doctype.estimation.estimation.get_rate",
            args: {
                item_code: d.item_code,
                warehouse: d.warehouse ? d.warehouse : ""
            },
            callback: function (r) {
                d.rate_raw_material = r.message[0]
                d.amount_raw_material = r.message[0] * d.qty_raw_material
                d.available_qty = r.message[1]
                cur_frm.refresh_field("raw_material")
            }
        })
    }

}
cur_frm.cscript.item_code = function (frm,cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.item_code){
        frappe.call({
            method: "service_pro.service_pro.doctype.estimation.estimation.get_rate",
            args: {
                item_code: d.item_code,
                warehouse: d.warehouse ? d.warehouse : ""
            },
            callback: function (r) {
                d.rate_raw_material = r.message[0]
                d.amount_raw_material = r.message[0] * d.qty_raw_material
                d.available_qty = r.message[1]
                cur_frm.refresh_field("raw_material")
            }
        })
    }

}
cur_frm.cscript.item_code_prod = function (frm,cdt, cdn) {
    var d = locals[cdt][cdn]
    if(cur_frm.doc.item_code_prod){
        frappe.call({
            method: "service_pro.service_pro.doctype.estimation.estimation.get_rate",
            args: {
                item_code: d.item_code_prod,
                warehouse: d.warehouse ? d.warehouse : ""
            },
            callback: function (r) {
                cur_frm.doc.rate = r.message[0]
                cur_frm.doc.amount = r.message[0] * cur_frm.doc.qty
                cur_frm.refresh_field("rate")
                cur_frm.refresh_field("amount")
            }
        })
    }

}
cur_frm.cscript.qty = function (frm,cdt, cdn) {
    cur_frm.doc.amount = cur_frm.doc.qty * cur_frm.doc.rate
    cur_frm.refresh_field("amount")
}
cur_frm.cscript.rate = function (frm,cdt, cdn) {
    cur_frm.doc.amount = cur_frm.doc.qty * cur_frm.doc.rate
        cur_frm.refresh_field("amount")

}

cur_frm.cscript.advance = function (frm,cdt, cdn) {
    cur_frm.call({
        doc: cur_frm.doc,
        method: 'generate_jv',
        freeze: true,
        freeze_message: "Generating Journal Entry ...",
        callback: () => {}
    })
}

