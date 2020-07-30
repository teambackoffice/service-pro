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
function compute_additional_cost(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.additional_cost.length;x += 1){
        total += cur_frm.doc.additional_cost[x].additional_cost_amount
    }
    cur_frm.doc.additional_cost_total = total
    cur_frm.refresh_field("additional_cost_total")
     set_rate_and_amount(cur_frm)
}
function compute_scoop_of_work_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.scoop_of_work.length;x += 1){
        total += cur_frm.doc.scoop_of_work[x].cost
    }
    cur_frm.doc.scoop_of_work_total = total
    cur_frm.refresh_field("scoop_of_work_total")
     set_rate_and_amount(cur_frm)
}
function compute_raw_material_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.raw_material.length;x += 1){
        total += cur_frm.doc.raw_material[x].amount_raw_material
    }
    cur_frm.doc.raw_material_total = total
    cur_frm.refresh_field("raw_material_total")
     set_rate_and_amount(cur_frm)
}

frappe.ui.form.on('Production', {
    onload: function (frm) {
        if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
            frm.set_df_property('series', 'options', ['HA-'])
            cur_frm.doc.series = "HA-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 0)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 0 )
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Assemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
	        frm.set_df_property('series', 'options', ['','SK-','HA-'])

            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)

        } else if(cur_frm.doc.type && cur_frm.doc.type === "Disassemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
	        frm.set_df_property('series', 'options', ['SK-D-'])
            cur_frm.doc.series = "SK-D-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
        }
        if(cur_frm.is_new()){
            if(cur_frm.doc.estimation){
                cur_frm.doc.type = "Service"
                 frm.set_df_property('series', 'options', ['HA-'])
                cur_frm.doc.series = "HA-"
                cur_frm.refresh_field("series")
                cur_frm.refresh_field("type")
            }
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
            frappe.db.get_single_value('Production Settings', 'rate_of_materials_based_on')
            .then(rate => {
                cur_frm.doc.rate_of_materials_based_on = rate
                cur_frm.refresh_field("rate_of_materials_based_on")
            })
            frappe.db.get_single_value('Production Settings', 'price_list')
            .then(price_list => {
                cur_frm.doc.price_list = price_list
                cur_frm.refresh_field("price_list")
            })
        }

        var status = frappe.meta.get_docfield("Scoop of Work", "status", cur_frm.doc.name);
        var qty = frappe.meta.get_docfield("Raw Material", "qty_raw_material", cur_frm.doc.name);
        var rate = frappe.meta.get_docfield("Raw Material", "rate_raw_material", cur_frm.doc.name);
        frappe.call({
            method: "service_pro.service_pro.doctype.production.production.get_se",
            args:{
                name: cur_frm.doc.name
            },
            callback: function (r) {
                if(r.message){
                    qty.read_only = 1
                    rate.read_only = 1
                }

            }
        })
        status.read_only = (cur_frm.doc.status === "Completed")

        cur_frm.set_df_property('advance_payment', 'read_only', cur_frm.doc.status === "Completed");

    },
    validate: function (frm) {
        frm.set_df_property('type', 'read_only', 1);

    },
	refresh: function() {
     cur_frm.set_df_property("scoop_of_work", "hidden", cur_frm.doc.type === "Assemble" || cur_frm.doc.type === "Disassemble" )
        cur_frm.set_df_property("scoop_of_work_total", "hidden", cur_frm.doc.type === "Assemble" || cur_frm.doc.type === "Disassemble" )


        cur_frm.set_query('expense_account',"advance_payment", () => {
            return {
                filters: [
                        ["account_type", "in", ["Bank","Cash"]]
                    ]
            }
        })
        cur_frm.set_query('expense_ledger',"additional_cost", () => {
            return {
                filters: [
                        ["account_type", "in", ["Expense Account"]]
                    ]
            }
        })
        cur_frm.set_query('production',"raw_material", () => {
            return {
                filters: {
                    docstatus: 1,
                    status: "In Progress"
                }
            }
        })
        if(cur_frm.doc.docstatus){
            frappe.call({
                method: "service_pro.service_pro.doctype.production.production.get_jv",
                args: {
                    production: cur_frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message)
                    if(r.message){
                        cur_frm.set_df_property('advance_payment', 'read_only', 1);
                        cur_frm.set_df_property('journal_entry', 'hidden', 0);
                        cur_frm.set_df_property('advance', 'hidden', 1);
                    } else {
                        cur_frm.set_df_property('advance_payment', 'read_only', 0);
                        cur_frm.set_df_property('journal_entry', 'hidden', 1);
                        cur_frm.set_df_property('advance', 'hidden', 0);
                    }
                }
            })
        } else if (cur_frm.is_new()){
            console.log("NEW")
            cur_frm.set_df_property('journal_entry', 'hidden', 1);
            cur_frm.set_df_property('advance', 'hidden', 1);
        }


	    cur_frm.set_query('income_account', () => {
            return {
                filters: {
                    is_group: 0,
                }
            }
        });

        var generate_button = true
        if(cur_frm.doc.scoop_of_work !== undefined){
             for(var x=0;x<cur_frm.doc.scoop_of_work.length;x += 1){
            if(cur_frm.doc.scoop_of_work[x].status === "In Progress"){
                generate_button = false
            }
        }
        }

        frappe.call({
                method: "service_pro.service_pro.doctype.production.production.get_se",
                args:{
                    name: cur_frm.doc.name
                },
                callback: function (r) {
                    if(!r.message && generate_button && cur_frm.doc.status === "In Progress" && cur_frm.doc.docstatus){
                            if(["Assemble", "Disassemble"].includes(cur_frm.doc.type) ){
                                if(cur_frm.doc.production_status === "Completed"){
                                    cur_frm.add_custom_button(__("Stock Entry"), () => {
                                         cur_frm.call({
                                            doc: cur_frm.doc,
                                            method: 'generate_se',
                                            freeze: true,
                                            freeze_message: "Generating Stock Entry...",
                                             async: false,
                                            callback: (r) => {
                                                cur_frm.reload_doc()

                                         }
                                        })
                                    }, "Generate");
                                }

                        } else {
                            cur_frm.add_custom_button(__("Stock Entry"), () => {
                             cur_frm.call({
                                doc: cur_frm.doc,
                                method: 'generate_se',
                                freeze: true,
                                freeze_message: "Generating Stock Entry...",
                                 async: false,
                                callback: (r) => {
                                    cur_frm.reload_doc()

                             }
                            })
                        }, "Generate");
                        }

                    } else if(r.message && generate_button && cur_frm.doc.status === "In Progress" && cur_frm.doc.docstatus){
                                                cur_frm.set_df_property('raw_material', 'read_only', 1);

                        frappe.call({
                            method: "service_pro.service_pro.doctype.production.production.get_dn_or_si",
                            args: {
                                name: cur_frm.doc.name,
                                doctype: "Sales Invoice"
                            },
                            callback: function (r) {
                                if (!r.message[0] && !r.message[1]) {
                                    cur_frm.add_custom_button(__("Sales Invoice"), () => {
                                        cur_frm.call({
                                            doc: cur_frm.doc,
                                            method: 'generate_si',
                                            freeze: true,
                                            freeze_message: "Generating Sales Invoice ...",
                                            callback: (r) => {
                                                                                    cur_frm.reload_doc()

                                                frappe.set_route("Form", "Sales Invoice", r.message);
                                            }
                                        })
                                    },"Generate");
                                    cur_frm.add_custom_button(__("Delivery Note"), () => {
                                        cur_frm.call({
                                            doc: cur_frm.doc,
                                            method: 'generate_dn',
                                            freeze: true,
                                            freeze_message: "Generating Delivery Note ...",
                                            callback: (r) => {
                                                                                    cur_frm.reload_doc()

                                                frappe.set_route("Form", "Delivery Note", r.message);
                                            }
                                        })
                                    },"Generate");
                                }
                            }
                        })

                    }

                }
            })
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

            frm.set_df_property('series', 'options', ['HA-'])
            cur_frm.doc.series = "HA-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 0)
                        cur_frm.set_df_property("scoop_of_work_total", "hidden", 0 )
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Assemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');
	        frm.set_df_property('series', 'options', ['','SK-','HA-'])

            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
                        cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)

        } else if(cur_frm.doc.type && cur_frm.doc.type === "Disassemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');

	        frm.set_df_property('series', 'options', ['SK-D-'])
            cur_frm.doc.series = "SK-D-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
        }
	},
    estimation: function(frm) {

	    if(cur_frm.doc.type && cur_frm.doc.type === "Service" && cur_frm.doc.estimation){
            get_items_from_estimation(frm,cur_frm)

        } else {
            cur_frm.doc.item_code_prod = undefined
            cur_frm.doc.qty = 1
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
        cur_frm.refresh_field("item_code_prod")
        cur_frm.refresh_field("qty")
        cur_frm.refresh_field("rate")
        cur_frm.refresh_field("amount")
        frappe.db.get_doc('Item', doc.item_code)
            .then(doc => {
                cur_frm.doc.umo = doc.stock_uom
                cur_frm.refresh_field("umo")

            })
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
            method: "service_pro.service_pro.doctype.production.production.get_rate",
            args: {
                item_code: d.item_code,
                warehouse: d.warehouse ? d.warehouse : "",
                based_on: cur_frm.doc.rate_of_materials_based_on ? cur_frm.doc.rate_of_materials_based_on : "",
                price_list: cur_frm.doc.price_list ? cur_frm.doc.price_list : ""

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
            method: "service_pro.service_pro.doctype.production.production.get_rate",
            args: {
                item_code: d.item_code,
                warehouse: d.warehouse ? d.warehouse : "",
                based_on: cur_frm.doc.rate_of_materials_based_on ? cur_frm.doc.rate_of_materials_based_on : "",
                price_list: cur_frm.doc.price_list ? cur_frm.doc.price_list : ""

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
cur_frm.cscript.item_code_prod = function (frm,cdt, cdn) {
    if(cur_frm.doc.item_code_prod){
        frappe.call({
            method: "service_pro.service_pro.doctype.production.production.get_uom",
            args: {
                item_code: cur_frm.doc.item_code_prod
            },
            callback: function (r) {
                cur_frm.doc.umo = r.message
                cur_frm.refresh_field("umo")
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
        callback: () => {
            cur_frm.refresh()
        }
    })
}

cur_frm.cscript.journal_entry = function (frm,cdt, cdn) {
    frappe.call({
            method: "service_pro.service_pro.doctype.production.production.get_jv",
            args: {
                production: cur_frm.doc.name
            },
            callback: function (r) {
                console.log(r.message)
                if(r.message){
                     frappe.set_route("Form", "Journal Entry", r.message);
                }
            }
        })
}
cur_frm.cscript.additional_cost_amount = function (frm,cdt, cdn) {
    compute_additional_cost(cur_frm)
}
function set_rate_and_amount(cur_frm) {
    cur_frm.doc.rate = cur_frm.doc.raw_material_total + cur_frm.doc.scoop_of_work_total + cur_frm.doc.additional_cost_total
    cur_frm.doc.amount = (cur_frm.doc.raw_material_total + cur_frm.doc.scoop_of_work_total + cur_frm.doc.additional_cost_total) * cur_frm.doc.qty
    cur_frm.refresh_field("amount")
    cur_frm.refresh_field("rate")
}