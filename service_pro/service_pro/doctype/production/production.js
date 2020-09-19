// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt
cur_frm.cscript.qty_raw_material = function (frm,cdt,cdn) {
    frappe.db.get_single_value('Stock Settings', 'allow_negative_stock')
        .then(ans => {
            var d = locals[cdt][cdn]
            if(d.production){
                frappe.call({
                    method: "service_pro.service_pro.doctype.production.production.get_available_qty",
                    args: {
                        production: d.production
                    },
                    async: false,
                    callback: function (r) {
                        if(d.qty_raw_material > r.message){
                            var qty_ = d.qty_raw_material
                             d.qty_raw_material = r.message

                            cur_frm.refresh_field("raw_material")
                            frappe.throw("Can't change Qty to " + qty_.toString() + ". Maximum Available qty is " + r.message.toString())
                        } else {
                              frappe.db.get_doc("Production", d.production)
                            .then(doc => {
                                if(doc.qty % d.qty_raw_material === 0){
                                    d.rate_raw_material = doc.rate / (doc.qty / d.qty_raw_material)
                                    d.amount_raw_material = doc.rate / (doc.qty / d.qty_raw_material)
                                } else {
                                    d.rate_raw_material = doc.rate / d.qty_raw_material
                                    d.amount_raw_material = doc.rate / d.qty_raw_material
                                }

                                cur_frm.refresh_field("raw_material")
                            })
                        }


                    }
                })

            } else {
                if((d.qty_raw_material && d.qty_raw_material <= d.available_qty) || ans){
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


            compute_raw_material_total(cur_frm)
            compute_for_selling_price(cur_frm)
set_item_selling_price(cur_frm)

        })

}
cur_frm.cscript.rate_raw_material = function (frm,cdt,cdn) {
   var d = locals[cdt][cdn]
    if(d.rate_raw_material){
        d.amount_raw_material = d.rate_raw_material * d.qty_raw_material
        cur_frm.refresh_field("raw_material")
    }
    compute_raw_material_total(cur_frm)
    compute_for_selling_price(cur_frm)
}
cur_frm.cscript.raw_material_add = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
   frappe.db.get_single_value('Production Settings', 'raw_material_warehouse')
        .then(warehouse => {
            if(warehouse){
                d.warehouse = warehouse
                cur_frm.refresh_field("raw_material")
            }
        })
    frappe.db.get_single_value('Production Settings', 'raw_material_cost_center')
        .then(cost_center => {
            if(cost_center){
                 d.cost_center = cost_center
                cur_frm.refresh_field("raw_material")
            } else {
                d.cost_center = cur_frm.doc.cost_center
                cur_frm.refresh_field("raw_material")
            }

        })
}
cur_frm.cscript.raw_material_remove = function (frm,cdt,cdn) {
    var d = frappe.get_doc(cdt, cdn);
        compute_raw_material_total(cur_frm)
        compute_for_selling_price(cur_frm)
    set_item_selling_price(cur_frm)
    if(cdn){
         cur_frm.call({
            doc: cur_frm.doc,
            method: 'change_production_status',
            args: {
              production: cdn
            },
            freeze: true,
            freeze_message: "Changing Production Status...",
             async: false,
            callback: (r) => {}
    }   )
    }

}
cur_frm.cscript.cost = function (frm,cdt,cdn) {
    compute_scoop_of_work_total(cur_frm)

}
cur_frm.cscript.value_of_good_solid = function (frm,cdt,cdn) {

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
    var total_cost = 0
    for(var x=0;x<cur_frm.doc.scoop_of_work.length;x += 1){
        if(cur_frm.doc.scoop_of_work[x].value_of_good_solid){
            total += cur_frm.doc.scoop_of_work[x].cost
        }

            total_cost += cur_frm.doc.scoop_of_work[x].cost

    }
    cur_frm.doc.scoop_of_work_total = total_cost
    cur_frm.doc.editable_total = total
    cur_frm.refresh_field("scoop_of_work_total")
    cur_frm.refresh_field("editable_total")
     set_rate_and_amount(cur_frm)
}
function compute_raw_material_total(cur_frm) {
    var amount = 0
    for(var x=0;x<cur_frm.doc.raw_material.length;x += 1){
        amount += cur_frm.doc.raw_material[x].amount_raw_material
    }
    cur_frm.doc.raw_material_amount = amount
    cur_frm.doc.raw_material_total =  amount / cur_frm.doc.qty
    cur_frm.refresh_field("raw_material_total")
    cur_frm.refresh_field("raw_material_amount")
     set_rate_and_amount(cur_frm)
}
cur_frm.cscript.cylinder_service = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.cylinder_service){
        console.log("CYLINDER SERVICE")
        frappe.db.get_doc("Production", d.cylinder_service)
            .then(prod => {
                cur_frm.doc.customer = prod.customer
                cur_frm.refresh_field("customer")
                cur_frm.trigger("customer")
            var names = Array.from(cur_frm.doc.linked_productions, x => "cylinder_service" in x ? x.cylinder_service:"")
             cur_frm.fields_dict.linked_productions.grid.get_field("cylinder_service").get_query =
                function() {
                    var filters =  [
                        ["name", "not in", names],
                        ["status", "!=", "Completed"],
                        ["docstatus", "=", 1],
                    ]
                    if(cur_frm.doc.customer){
                        filters.push(["customer", "=", cur_frm.doc.customer])
                    }
                    if(cur_frm.doc.type === 'Re-Service'){
                        filters.push(["series", "in", ["CS-", "SK-", "HK-", "PB-"]])
                    } else {
                        filters.push(["series", "=", "CS-"])
                    }
                    return {
                         filters: filters
                    }
                }
        })
    }
}
function showPosition(position) {
  console.log("Latitude: " + position.coords.latitude)
    console.log("Longitude: " + position.coords.longitude)
}
frappe.ui.form.on('Production', {
    onload_post_render: function(frm) {
if(!cur_frm.is_new()) {
    document.querySelectorAll("[data-doctype='Sales Invoice']")[1].style.display = "none";
    document.querySelectorAll("[data-doctype='Delivery Note']")[1].style.display = "none";
    document.querySelectorAll("[data-doctype='Stock Entry']")[1].style.display = "none";
}

        },
    onload: function (frm) {
        navigator.geolocation.getCurrentPosition(showPosition);
        if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
            frm.set_df_property('series', 'options', ['CS-'])
            cur_frm.doc.series = "CS-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 0)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 0 )
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Assemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
	        frm.set_df_property('series', 'options', ['','SK-','HA-','PB-'])

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
        } else if(cur_frm.doc.type && cur_frm.doc.type === "Re-Service") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
	        frm.set_df_property('series', 'options', ['RCS-', 'RSK-', 'RHA-', 'RPB-'])
            cur_frm.doc.series = "RCS-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
        }
        if(cur_frm.is_new()){
            if(cur_frm.doc.estimation){
                cur_frm.doc.type = "Service"
                 frm.set_df_property('series', 'options', ['CS-'])
                cur_frm.doc.series = "CS-"
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
        cur_frm.set_df_property('raw_material', 'read_only', cur_frm.doc.status === "Completed");


    },
    validate: function (frm) {
        frm.set_df_property('type', 'read_only', 1);

    },
	refresh: function(frm) {
        cur_frm.get_field("item_selling_price_list").grid.cannot_add_rows = true;
cur_frm.get_field("item_selling_price_list").grid.only_sortable();
cur_frm.refresh_field("item_selling_price_list")
         if(cur_frm.doc.docstatus && cur_frm.doc.status === "In Progress"){
             frm.add_custom_button(__("Close"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "Closed"
                        },
                        freeze: true,
                        freeze_message: "Closing...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
        } else if (cur_frm.doc.docstatus && cur_frm.doc.status === "Closed"){
            frm.add_custom_button(__("Open"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "Open"
                        },
                        freeze: true,
                        freeze_message: "Opening...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
        } else if (cur_frm.doc.docstatus && cur_frm.doc.status !== "Completed" && frappe.boot.user.roles.includes("System Manager")) {
            frm.add_custom_button(__("Complete"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "Completed"
                        },
                        freeze: true,
                        freeze_message: "Completing...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
         }
                console.log("NA MAN")
         if(cur_frm.doc.docstatus){
         frappe.call({
            method: "service_pro.service_pro.doctype.production.production.get_dn_si_qty",
            args: {
                item_code: cur_frm.doc.item_code_prod,
                qty: cur_frm.doc.qty,
                name: cur_frm.doc.name
            },
             async: false,
            callback: function (r) {
                console.log("ASDJALKSD")
                console.log(r.message)
                cur_frm.doc.qty_for_sidn = r.message
                cur_frm.refresh_field("qty_for_sidn")
            }
        })}
    // if(parseFloat(cur_frm.doc.qty_for_sidn) > 0 && parseFloat(cur_frm.doc.qty_for_sidn) < cur_frm.doc.qty && cur_frm.doc.docstatus){
    //     console.log("NA MAN")
    //     frappe.call({
    //         method: "service_pro.service_pro.doctype.production.production.change_status",
    //         args: {
    //             name: cur_frm.doc.name
    //         },
    //         callback: function () {}
    //     })
    // }
     cur_frm.set_df_property("scoop_of_work", "hidden", cur_frm.doc.type === "Assemble" || cur_frm.doc.type === "Disassemble" )
        cur_frm.set_df_property("scoop_of_work_total", "hidden", cur_frm.doc.type === "Assemble" || cur_frm.doc.type === "Disassemble" )

        frappe.call({
            method: "service_pro.service_pro.doctype.production.production.get_se",
            args:{
                name: cur_frm.doc.name
            },
            callback: function (r) {
                if(r.message){
                    frm.set_df_property('production_status', 'read_only', 1);
                    frm.set_df_property('additional_cost', 'read_only', 1);
                    cur_frm.set_df_property('invoice_rate', 'read_only', 1);

                } else {
                    cur_frm.set_df_property('invoice_rate', 'read_only', 0);
                }

            }
        })
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
                filters: [
                    ["name", "!=", cur_frm.doc.name],
                    ["series", "=", "SK-"],
                    ["docstatus", "=", 1],
                    ["status", "in", ["To Deliver and Bill","Linked"]]
                ]
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
            cur_frm.doc.status = "In Progress"
            cur_frm.refresh_field("status")
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
         cur_frm.set_query('cost_center', () => {
            return {
                filters: {
                    is_group: 0,
                }
            }
        });
         cur_frm.fields_dict.linked_productions.grid.get_field("cylinder_service").get_query =
			function() {
				return {
					 filters: [
                    ["status", "!=", "Completed"],
                    ["docstatus", "=", 1],
                    ["series", "=", "CS-"],
                ]
				}
			}

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
                    if(!r.message && generate_button && ["In Progress", "Partially Completed", "Partially Delivered"].includes(cur_frm.doc.status) && cur_frm.doc.docstatus){
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

                    } else if(r.message && generate_button && ["In Progress", "Partially Completed", "Partially Delivered", "To Deliver", "To Bill", "To Deliver and Bill"].includes(cur_frm.doc.status) && cur_frm.doc.docstatus && cur_frm.doc.type !== "Re-Service"){
                        cur_frm.set_df_property('raw_material', 'read_only', 1);
                        cur_frm.set_df_property('scoop_of_work', 'read_only', 1);

                        frappe.call({
                            method: "service_pro.service_pro.doctype.production.production.get_dn_or_si",
                            args: {
                                name: cur_frm.doc.name,
                                doctype: "Sales Invoice"
                            },
                            callback: function (r) {
                                if (cur_frm.doc.qty_for_sidn > 0) {

                                    cur_frm.add_custom_button(__("Sales Invoice"), () => {
                                        let d = new frappe.ui.Dialog({
                                        title: "Enter Qty",
                                        fields: [
                                            {
                                                label: 'Qty',
                                                fieldname: 'qty',
                                                fieldtype: 'Float',
                                                default: cur_frm.doc.qty_for_sidn
                                            }
                                        ],
                                        primary_action_label: 'Generate',
                                        primary_action(values) {

                                            cur_frm.doc.input_qty = values.qty
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
                                        }
                                    });

                                    d.show();

                                    },"Generate");

                                }
                                if( cur_frm.doc.qty_for_sidn > 0){
                                    cur_frm.add_custom_button(__("Delivery Note"), () => {
                                        let d = new frappe.ui.Dialog({
                                        title: "Enter Qty",
                                        fields: [
                                            {
                                                label: 'Qty',
                                                fieldname: 'qty',
                                                fieldtype: 'Float',
                                                default: cur_frm.doc.qty_for_sidn
                                            }
                                        ],
                                        primary_action_label: 'Generate',
                                        primary_action(values) {

                                            cur_frm.doc.input_qty = values.qty
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
                                        }
                                    });

                                    d.show();

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
                        var address = ""
                        if(r.message.address_line1){
                            address += r.message.address_line1
                            address += "\n"
                        }
                        if(r.message.city){
                            address += r.message.city
                            address += "\n"
                        }
                        if(r.message.county){
                            address += r.message.county
                            address += "\n"
                        }
                        if(r.message.country){
                            address += r.message.country
                            address += "\n"
                        }
                        if(r.message.state){
                            address += r.message.state
                            address += "\n"
                        }
                        if(r.message.pincode){
                            address += r.message.pincode
                            address += "\n"
                        }

                        cur_frm.doc.address_name = address
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

            frm.set_df_property('series', 'options', ['CS-'])
            cur_frm.doc.series = "CS-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 0)
                        cur_frm.set_df_property("scoop_of_work_total", "hidden", 0 )

        } else if(cur_frm.doc.type && cur_frm.doc.type === "Assemble") {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');
	        frm.set_df_property('series', 'options', ['','SK-','HA-', 'PB-'])

            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
            cur_frm.set_df_property("editable_total", "hidden", 1)
            cur_frm.set_df_property("section_break_21", "hidden", 1)
            cur_frm.set_df_property("section_break111", "hidden", 1)
            cur_frm.clear_table("linked_productions")
            cur_frm.refresh_field("linked_productions")
            cur_frm.fields_dict.linked_productions.grid.get_field("cylinder_service").get_query =
			function() {
				return {
					 filters: [
                    ["status", "!=", "Completed"],
                    ["docstatus", "=", 1],
                    ["series", "=", "CS-"],
                ]
				}
			}

        } else if(cur_frm.doc.type && cur_frm.doc.type === "Disassemble") {

	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');

	        frm.set_df_property('series', 'options', ['SK-D-'])
            cur_frm.doc.series = "SK-D-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
            cur_frm.set_df_property("editable_total", "hidden", 1)
            cur_frm.set_df_property("section_break_21", "hidden", 1)
            cur_frm.set_df_property("section_break111", "hidden", 1)
            cur_frm.clear_table("linked_productions")
            cur_frm.refresh_field("linked_productions")
            cur_frm.fields_dict.linked_productions.grid.get_field("cylinder_service").get_query =
			function() {
				return {
					 filters: [
                    ["status", "!=", "Completed"],
                    ["docstatus", "=", 1],
                    ["series", "=", "CS-"],
                ]
				}
			}

        } else if(cur_frm.doc.type && cur_frm.doc.type === "Re-Service") {

	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');

	        frm.set_df_property('series', 'options', ['RCS-', 'RSK-', 'RHA-', 'RPB-'])
            cur_frm.doc.series = "RCS-"
            cur_frm.refresh_field("series")
            cur_frm.set_df_property("scoop_of_work", "hidden", 1)
            cur_frm.set_df_property("scoop_of_work_total", "hidden", 1)
            cur_frm.clear_table("linked_productions")
            cur_frm.refresh_field("linked_productions")
            cur_frm.fields_dict.linked_productions.grid.get_field("cylinder_service").get_query =
			function() {
				return {
					 filters: [
                    ["status", "=", "Completed"],
                    ["docstatus", "=", 1],
                    ["series", "in", ["CS-", "SK-", "HK-", "PB-"]],
                ]
				}
			}

        }
	},
    estimation: function(frm) {

	    if(cur_frm.doc.type && cur_frm.doc.type === "Service" && cur_frm.doc.estimation){
            get_items_from_estimation(frm,cur_frm)
        } else {
            cur_frm.doc.item_code_prod = undefined
            cur_frm.doc.qty = 1
            cur_frm.doc.qty_for_sidn = 1
            cur_frm.doc.rate = 0
            cur_frm.doc.amount = 0
            cur_frm.refresh_field("item_code")
            cur_frm.refresh_field("qty")
            cur_frm.refresh_field("qty_for_sidn")
            cur_frm.refresh_field("rate")
            cur_frm.refresh_field("amount")

        }
	},
    address: function(frm) {
        if(cur_frm.doc.address){
            frappe.db.get_doc("Address", cur_frm.doc.address)
            .then(doc => {
                console.log(doc)
                var address = ""
                if(doc.address_line1){
                    address += doc.address_line1
                    address += "\n"
                }
                if(doc.city){
                    address += doc.city
                    address += "\n"
                }
                if(doc.county){
                    address += doc.county
                    address += "\n"
                }
                if(doc.country){
                    address += doc.country
                    address += "\n"
                }
                if(doc.state){
                    address += doc.state
                    address += "\n"
                }
                if(doc.pincode){
                    address += doc.pincode
                    address += "\n"
                }
                cur_frm.doc.address_name = address

                cur_frm.refresh_field("address_name")
            })
        }

	},

});

function filter_link_field(cur_frm) {
     cur_frm.set_query('estimation', () => {
        return {
            filters: [
                ["docstatus","=",1],
                ["status","=","To Production"]
            ]
        }
    })
}
function get_items_from_estimation(frm,cur_frm) {
   frappe.db.get_doc('Estimation', cur_frm.doc.estimation)
    .then(doc => {
        set_scoop_of_work(doc,frm)
        set_raw_material(doc,frm)
            console.log("asaaaaaa")
        cur_frm.doc.customer = doc.customer
        cur_frm.trigger('customer');
        cur_frm.doc.item_code_prod = doc.item_code_est
        cur_frm.doc.item_name = doc.item_name
        cur_frm.doc.qty = doc.qty
        cur_frm.doc.qty_for_sidn = doc.qty
        cur_frm.doc.rate = doc.rate
    console.log("QTY")
    console.log(doc.qty)
    console.log("INVOICE RATE")
    console.log("QTY")
        cur_frm.doc.amount = doc.qty * cur_frm.doc.invoice_rate
        cur_frm.refresh_field("item_code_prod")
        cur_frm.refresh_field("customer")
        cur_frm.refresh_field("item_name")
        cur_frm.refresh_field("qty")
        cur_frm.refresh_field("qty_for_sidn")
        cur_frm.refresh_field("rate")
        cur_frm.refresh_field("amount")

        frappe.db.get_doc('Item', doc.item_code_est)
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
            cost: row.cost
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
            umo: row.umo,
            item_name: row.item_name,
            warehouse: row.warehouse,
            available_qty: row.available_qty,
            qty_raw_material: row.qty_raw_material,
            rate_raw_material: row.rate_raw_material,
            amount_raw_material: row.amount_raw_material,
            cost_center: row.cost_center
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
                                compute_raw_material_total(cur_frm)

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
                 frappe.db.get_doc("Item", d.item_code)
                    .then(doc => {
                        console.log("NAA MAN")
                        d.item_name= doc.item_name
                       d.umo = doc.stock_uom

                        cur_frm.refresh_field("raw_material")
                set_item_selling_price(cur_frm)
                    })
                d.rate_raw_material = r.message[0]
                d.amount_raw_material = r.message[0] * d.qty_raw_material
                d.available_qty = r.message[1]
                cur_frm.refresh_field("raw_material")
                compute_raw_material_total(cur_frm)
                compute_for_selling_price(cur_frm)
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
                cur_frm.doc.umo = r.message[0]
                cur_frm.doc.item_name = r.message[1]
                cur_frm.refresh_field("item_name")
                cur_frm.refresh_field("umo")
            }
        })
    }

}
cur_frm.cscript.qty = function (frm,cdt, cdn) {
    cur_frm.doc.amount = cur_frm.doc.qty * cur_frm.doc.invoice_rate
    cur_frm.refresh_field("amount")
    compute_for_selling_price(cur_frm)
    compute_raw_material_total(cur_frm)

}
cur_frm.cscript.invoice_rate = function (frm,cdt, cdn) {
    cur_frm.doc.amount = cur_frm.doc.qty * cur_frm.doc.invoice_rate
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
cur_frm.cscript.editable_total = function (frm,cdt, cdn) {
    set_rate_and_amount(cur_frm)
}
function set_rate_and_amount(cur_frm) {
    cur_frm.doc.rate = cur_frm.doc.raw_material_total + cur_frm.doc.editable_total + cur_frm.doc.additional_cost_total
    cur_frm.doc.amount = cur_frm.doc.invoice_rate * cur_frm.doc.qty
    cur_frm.refresh_field("amount")
    cur_frm.refresh_field("rate")
}

function compute_for_selling_price(cur_frm) {
if(cur_frm.doc.raw_material !== undefined){
    frappe.call({
                method: "service_pro.service_pro.doctype.production.production.compute_selling_price",
                args: {
                    raw_materials: cur_frm.doc.raw_material,
                },
                async: false,
                callback: function (r) {
                   cur_frm.doc.total_selling_price = r.message
                    cur_frm.doc.total_selling_price__qty = r.message / cur_frm.doc.qty
                    cur_frm.refresh_field("total_selling_price")
                    cur_frm.refresh_field("total_selling_price__qty")
                }
            })
}



}

cur_frm.cscript.production = function (frm,cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.production){
        frappe.db.get_doc('Production', d.production)
            .then(prod => {
                frappe.call({
                    method: "service_pro.service_pro.doctype.production.production.get_available_qty",
                    args: {
                        production: d.production
                    },
                    callback: function (r) {
                        d.qty_raw_material = r.message

                        if(prod.qty % d.qty_raw_material === 0){
                            d.rate_raw_material = prod.rate / (prod.qty / d.qty_raw_material)
                            d.amount_raw_material = prod.rate / (prod.qty / d.qty_raw_material)
                        } else {
                            d.rate_raw_material = prod.rate / d.qty_raw_material
                            d.amount_raw_material = prod.rate / d.qty_raw_material
                        }
                        cur_frm.refresh_field("raw_material")
                        compute_raw_material_total(cur_frm)
                        compute_for_selling_price(cur_frm)
                    }
                })


            })
    }

}

cur_frm.cscript.material_request = function () {
    frappe.set_route('Form', 'Material Request', "New Material Request 1")
}

function set_item_selling_price(cur_frm) {
    console.log(cur_frm.doc.raw_material)


    if(cur_frm.doc.raw_material.length > 0){
        cur_frm.clear_table("item_selling_price_list")
        cur_frm.refresh_field("item_selling_price_list")
        !cur_frm.fields_dict['section_break_44'].collapse();
        frappe.call({
            method: "service_pro.service_pro.doctype.production.production.selling_price_list",
            args:{
                raw_materials: cur_frm.doc.raw_material
            },
            async: false,
            callback: function (r) {
                for(var x=0;x<r.message.length; x += 1){
                    cur_frm.add_child('item_selling_price_list', {
                        item_name: r.message[x].item_name,
                        qty: r.message[x].qty_raw_material,
                        selling_rate: r.message[x].rate_raw_material
                    });
                    cur_frm.refresh_field("item_selling_price_list")


                }
            }
        })

    } else {

        cur_frm.clear_table("item_selling_price_list")
        cur_frm.refresh_field("item_selling_price_list")
    }

    console.log("HUMAN")
}