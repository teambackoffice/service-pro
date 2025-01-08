// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt
var defaults = {}
cur_frm.cscript.inspection = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.inspection){
        var names = Array.from(cur_frm.doc.inspections, x => "inspection" in x ? x.inspection:"")
        cur_frm.fields_dict.inspections.grid.get_field("inspection").get_query =
			function() {
				return {
					filters: [
                    	["item_code", "=", d.item_code],
                        ["service_receipt_note", "=", cur_frm.doc.receipt_note],
                    	["docstatus", "=", 1],
                           ["status", "in", ["To Estimation", "To Quotation"]],
                    	["name", "not in", names]
					]
				}
			}

			if(cur_frm.doc.qty > 0){
                cur_frm.doc.qty  += 1
                cur_frm.refresh_field("qty")
                                set_rate_and_amount(cur_frm)

            } else {
			    frappe.db.get_doc("Inspection", d.inspection)
                    .then(doc => {
                      cur_frm.doc.item_code_est = doc.item_code
                      cur_frm.doc.qty = 1
                cur_frm.trigger("item_code_est")
                cur_frm.refresh_field("qty")
                cur_frm.refresh_field("item_code_est")
                set_rate_and_amount(cur_frm)
                    })
            }
    }
}
frappe.ui.form.on('Estimation', {
    raw_material_total: function(frm) {
        calculate_total_costs(frm);
    },
    total_cost_amount: function(frm) {
        calculate_total_costs(frm);
    },

    setup: function(frm){
        frm.fields_dict['raw_material'].grid.get_field('cost_center').get_query = function (doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
    },
    raw_material_total: function(frm) {
        calculate_total_cost(frm);
    },
    total_cost_amount: function(frm) {
        calculate_total_cost(frm);
    },
    
    
    receipt_note: function () {
        if(cur_frm.doc.receipt_note){
            cur_frm.fields_dict.inspections.grid.get_field("inspection").get_query =
			function() {
				return {
					filters: [
                    	["service_receipt_note", "=", cur_frm.doc.receipt_note],
                    	["docstatus", "=", 1],
                        ["status", "in", ["To Quotation","To Estimation"]]
					]
				}
			}
        }

    },
    
    customer: function () {
	    if(cur_frm.doc.customer){
	         frappe.db.get_doc("Customer", cur_frm.doc.customer)
            .then(doc => {
                cur_frm.doc.customer_name = doc.customer_name
                cur_frm.refresh_field("customer_name")
            })
        }

    },
    refresh: function (frm) { 
        calculate_total_costs(frm);
        frm.add_custom_button(__('Quotation'), function () {
            frappe.call({
                method: "service_pro.service_pro.doctype.estimation.estimation.create_production",
                args: {
                    source_name: frm.doc.name
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__('Quotation {0} created successfully.', [r.message]));
                        frappe.set_route("Form", "Quotation", r.message);
                    }
                }
            });
        }, __("Create"));
        

        cur_frm.set_query('receipt_note', () => {
            return {
                filters: [
                    ["docstatus", "=", 1],
                    ["status", "in", ["To Quotation", "To Estimation"]]
                ]
            };
        });

        if (cur_frm.doc.docstatus && !(["Closed", "Completed"].includes(cur_frm.doc.status))) {
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
                        cur_frm.reload_doc();
                    }
                });
            });
        }
        else if (cur_frm.doc.status === "Closed") {
            frm.add_custom_button(__("Open"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                        status: "To Quotation"
                    },
                    freeze: true,
                    freeze_message: "Opening...",
                    callback: () => {
                        cur_frm.reload_doc();
                    }
                });
            });
        }

        cur_frm.add_custom_button(__("Material Request"), () => {
            frappe.new_doc('Material Request');
        });

        frm.fields_dict['workshop_details'].grid.get_field('machine_name').get_query = function (doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
    },
   

    company: function (frm) {
        frm.fields_dict['workshop_details'].grid.get_field('machine_name').get_query = function (doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
    },
    company: function () {
       if(cur_frm.doc.company){
            cur_frm.call({
                doc: cur_frm.doc,
                method: "get_defaults",
                freeze: true,
                freeze_message: "Getting Company Defaults....",
                callback: function (r) {
                    defaults = r.message

                }
            })
        }
    },
	onload: function(frm) {
        if(cur_frm.doc.company){
            cur_frm.call({
                doc: cur_frm.doc,
                method: "get_defaults",
                freeze: true,
                freeze_message: "Getting Company Defaults....",
                callback: function (r) {
                    defaults = r.message

                }
            })
        }

         // frappe.db.get_single_value('Production Settings', 'rate_of_materials_based_on')
         //    .then(rate => {
         //        cur_frm.doc.rate_of_materials_based_on = rate
         //        cur_frm.refresh_field("rate_of_materials_based_on")
         //    })
         //    frappe.db.get_single_value('Production Settings', 'price_list')
         //    .then(price_list => {
         //        cur_frm.doc.price_list = price_list
         //        cur_frm.refresh_field("price_list")
         //    })
	    var df = frappe.meta.get_docfield("Scoop of Work", "status", cur_frm.doc.name);
	    var df0 = frappe.meta.get_docfield("Scoop of Work", "value_of_good_solid", cur_frm.doc.name);
	    var df1 = frappe.meta.get_docfield("Raw Material", "production", cur_frm.doc.name);
        df.in_grid_view = 0
        df.hidden = 1
        df1.hidden = 1
        df0.hidden = 1
	}
});

function calculate_total_costs(frm) {
    const raw_material_total = parseFloat(frm.doc.raw_material_total || 0);
    const total_cost_amount = parseFloat(frm.doc.total_cost_amount || 0);

    const total_cost = raw_material_total + total_cost_amount;

    frm.set_value('total_cost', total_cost);


    if (frm.doc.scoop_of_work) {
        frm.doc.scoop_of_work.forEach(row => {
            frappe.model.set_value(row.doctype, row.name, 'cost', total_cost);
        });

        frm.refresh_field('scoop_of_work');
    }
}

function calculate_total_cost(frm) {
    // Ensure the fields are numbers, fallback to 0 if undefined
    const raw_material_total = parseFloat(frm.doc.raw_material_total || 0);
    const total_cost_amount = parseFloat(frm.doc.total_cost_amount || 0);

    // Calculate total_cost
    frm.set_value('total_cost', raw_material_total + total_cost_amount);
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
cur_frm.cscript.item_code_est = function (frm,cdt, cdn) {

       frappe.db.get_doc("Item", cur_frm.doc.item_code_est)
        .then(doc => {
           cur_frm.doc.item_name = doc.item_name
            cur_frm.refresh_field("item_name")
        })
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
                       d.item_name = doc.item_name
                       d.umo = doc.stock_uom
                        cur_frm.refresh_field("raw_material")
                    })
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
    cur_frm.doc.total_cost = total
    cur_frm.refresh_field("total_cost")
    set_rate_and_amount(cur_frm)
}
function compute_raw_material_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.raw_material.length;x += 1){
        total += cur_frm.doc.raw_material[x].amount_raw_material + cur_frm.doc.scoop_of_work[x].cost
    }
    cur_frm.doc.raw_material_total = total
    cur_frm.refresh_field("raw_material_total")
    set_rate_and_amount(cur_frm)
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
    // frappe.db.get_single_value('Production Settings', 'raw_material_warehouse')
    //     .then(warehouse => {
    d.warehouse = defaults['raw_material_defaults'].warehouse
    cur_frm.refresh_field("raw_material")
        // })
}
cur_frm.cscript.scoop_of_work_total = function (frm,cdt,cdn) {
   set_rate_and_amount(cur_frm)
}
function set_rate_and_amount(cur_frm) {
    cur_frm.doc.rate = cur_frm.doc.raw_material_total + cur_frm.doc.scoop_of_work_total
    cur_frm.doc.amount = (cur_frm.doc.raw_material_total + cur_frm.doc.scoop_of_work_total) * cur_frm.doc.qty
    cur_frm.refresh_field("amount")
    cur_frm.refresh_field("rate")
}




frappe.ui.form.on('Workshop Details', {
    from_time: function (frm, cdt, cdn) {
        update_to_time_and_hours(frm, cdt, cdn);
        calculate_totals(frm);
    },
    to_time: function (frm, cdt, cdn) {
        update_hours_based_on_times(frm, cdt, cdn);
        calculate_totals(frm);
    },
    hrs: function (frm, cdt, cdn) {
        update_cost_amount(frm, cdt, cdn);
        update_worker_cost_amount(frm, cdt, cdn);
        calculate_totals(frm);
    },
    machine_name: function (frm, cdt, cdn) {
        update_cost_amount(frm, cdt, cdn);
        calculate_totals(frm);
    },
    worker: function (frm, cdt, cdn) {
        update_worker_cost_amount(frm, cdt, cdn);
        calculate_totals(frm);
    },
    total_machine_cost: function (frm, cdt, cdn) {
        calculate_totals(frm);
    },
    total_worker_cost: function (frm, cdt, cdn) {
        calculate_totals(frm);
    },
    workshop_details_remove: function (frm) {
        calculate_totals(frm);
    }
});

const validate_time_format = (time, fieldName) => {
    const formattedTime = moment(time, "YYYY-MM-DD HH:mm:ss");
    if (!formattedTime.isValid()) {
        frappe.msgprint(__(`Invalid datetime format in "${fieldName}". Please use "YYYY-MM-DD HH:mm:ss" format.`));
        return false;
    }
    return formattedTime;
};

const update_to_time_and_hours = (frm, cdt, cdn) => {
    const child = locals[cdt][cdn];
    if (!child.from_time || !child.hrs) return;

    const fromTime = validate_time_format(child.from_time, "From Time");
    if (!fromTime) return;

    const toTime = moment(fromTime).add(child.hrs, "hours").format("YYYY-MM-DD HH:mm:ss");
    frappe.model.set_value(cdt, cdn, "to_time", toTime);

    update_cost_amount(frm, cdt, cdn);
    update_worker_cost_amount(frm, cdt, cdn);
};

const update_hours_based_on_times = (frm, cdt, cdn) => {
    const child = locals[cdt][cdn];
    if (!child.from_time || !child.to_time) {
        frappe.msgprint(__('Both "From Time" and "To Time" must be set to calculate hours.'));
        return;
    }

    
    const fromTime = validate_time_format(child.from_time, "From Time");
    const toTime = validate_time_format(child.to_time, "To Time");

    if (!fromTime || !toTime) return;

    const calculatedHours = moment(toTime).diff(moment(fromTime), "seconds") / 3600;
    frappe.model.set_value(cdt, cdn, "hrs", calculatedHours.toFixed(2));

    update_cost_amount(frm, cdt, cdn);
    update_worker_cost_amount(frm, cdt, cdn);
};

const update_cost_amount_field = (frm, cdt, cdn) => {
    const row = locals[cdt][cdn];
    const totalMachineCost = parseFloat(row.total_machine_cost || 0);
    const totalWorkerCost = parseFloat(row.total_worker_cost || 0);

    const costAmount = totalMachineCost + totalWorkerCost;
    frappe.model.set_value(cdt, cdn, "cost_amount", costAmount);
};

const update_cost_amount = (frm, cdt, cdn) => {
    const row = locals[cdt][cdn];
    if (row.machine_name && row.hrs) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Machine",
                filters: { name: row.machine_name },
                fieldname: "cost_rate"
            },
            callback: function (r) {
                if (r.message) {
                    const costRate = r.message.cost_rate || 0;
                    const costAmount = costRate * row.hrs;

                    frappe.model.set_value(cdt, cdn, "cost_rate", costRate);
                    frappe.model.set_value(cdt, cdn, "total_machine_cost", costAmount);
                    update_cost_amount_field(frm, cdt, cdn);
                }
            }
        });
    } else {
        frappe.model.set_value(cdt, cdn, "total_machine_cost", 0);
        update_cost_amount_field(frm, cdt, cdn);
    }
};

const update_worker_cost_amount = (frm, cdt, cdn) => {
    const row = locals[cdt][cdn];
    if (row.worker && row.hrs) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Worker",
                filters: { name: row.worker },
                fieldname: "worker_per_hour_cost"
            },
            callback: function (r) {
                if (r.message) {
                    const workerRate = r.message.worker_per_hour_cost || 0;
                    const workerCostAmount = workerRate * row.hrs;

                    frappe.model.set_value(cdt, cdn, "worker_per_hour_cost", workerRate);
                    frappe.model.set_value(cdt, cdn, "total_worker_cost", workerCostAmount);
                    update_cost_amount_field(frm, cdt, cdn);
                }
            }
        });
    } else {
        frappe.model.set_value(cdt, cdn, "total_worker_cost", 0);
        update_cost_amount_field(frm, cdt, cdn);
    }
};

const calculate_totals = (frm) => {
    let totalHours = 0;
    let totalMachineCost = 0;
    let totalWorkerHours = 0;
    let totalCostAmount = 0;

    (frm.doc.workshop_details || []).forEach(row => {
        totalHours += parseFloat(row.hrs || 0);
        totalMachineCost += parseFloat(row.total_machine_cost || 0);
        totalWorkerHours += parseFloat(row.hrs || 0);  
        totalCostAmount += parseFloat(row.cost_amount || 0); 
    });

    frm.set_value('total_machine_hours', totalHours.toFixed(2));
    frm.set_value('total_cost_amount', totalCostAmount.toFixed(2));
    frm.set_value('total_worker_hours', totalWorkerHours.toFixed(2));  
};


