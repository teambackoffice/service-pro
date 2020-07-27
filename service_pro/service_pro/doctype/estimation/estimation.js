// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Estimation', {
	onload: function(frm) {
	    var df = frappe.meta.get_docfield("Scoop of Work", "status", cur_frm.doc.name);
	    if (cur_frm.doc.doctype === "Estimation"){
	        df.in_grid_view = 0
            df.hidden = 1
        } else if (cur_frm.doc.doctype === "Production") {
	        df.in_grid_view = 1
	        df.hiddne = 0
        }
        frappe.call({
            method: "service_pro.service_pro.doctype.estimation.estimation.get_dimensions",
            args:{},
            callback: function (r) {
                frm.set_df_property('rod_dia', 'options', r.message[0])
                frm.set_df_property('r_length', 'options', r.message[1])
                frm.set_df_property('tube_size', 'options', r.message[2])
                frm.set_df_property('t_length', 'options', r.message[3])
            }
        })
	},
});

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
                compute_raw_material_total(cur_frm)
            }
        })

    }

}
cur_frm.cscript.qty_raw_material = function (frm,cdt, cdn) {
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

}
cur_frm.cscript.rate_raw_material = function (frm,cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.rate_raw_material){
        d.amount_raw_material = d.rate_raw_material * d.qty_raw_material
        cur_frm.refresh_field("raw_material")
    }

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
cur_frm.cscript.cost = function (frm,cdt,cdn) {
    compute_scoop_of_work_total(cur_frm)
}
cur_frm.cscript.scoop_of_work_remove = function (frm,cdt,cdn) {
    compute_scoop_of_work_total(cur_frm)
}

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
cur_frm.cscript.raw_material_remove = function (frm,cdt,cdn) {
    compute_raw_material_total(cur_frm)
}
cur_frm.cscript.raw_material_add = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
    frappe.db.get_single_value('Production Settings', 'raw_material_warehouse')
        .then(warehouse => {
            d.warehouse = warehouse
            cur_frm.refresh_field("raw_material")
        })
}