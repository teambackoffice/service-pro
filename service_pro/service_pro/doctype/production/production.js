// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt
cur_frm.cscript.raw_material_add = function (frm,cdt,cdn) {
    var d = locals[cdt][cdn]
    d.warehouse = cur_frm.doc.raw_material_warehouse
    cur_frm.refresh_field("raw_material")
}
frappe.ui.form.on('Production', {

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
	},
    customer: function() {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
        }
	},
    type: function(frm) {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service"){
            filter_link_field(cur_frm)
        } else {
	        cur_frm.doc.estimation = ""
            cur_frm.refresh_field("estimation")
            frm.trigger('estimation');
        }
	},
    estimation: function(frm) {
	    if(cur_frm.doc.type && cur_frm.doc.type === "Service" && cur_frm.doc.estimation){
            get_and_set_finished_item(frm,cur_frm)
        } else {
            cur_frm.doc.item_code = undefined
            cur_frm.doc.qty = 0
            cur_frm.doc.rate = 0
            cur_frm.doc.amount = 0
            cur_frm.refresh_field("item_code")
            cur_frm.refresh_field("qty")
            cur_frm.refresh_field("rate")
            cur_frm.refresh_field("amount")
            set_property_finished_item_fields(frm,cur_frm)

        }
	},
    on_submit: function(frm) {
        for(var x=0;x < cur_frm.doc.scoop_of_work.length;x += 1){
            cur_frm.doc.scoop_of_work[x].status = "In Progress"
            cur_frm.refresh_field("scoop_of_work")
        }
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
function get_and_set_finished_item(frm,cur_frm) {
   frappe.db.get_doc('Estimation', cur_frm.doc.estimation)
    .then(doc => {
        set_scoop_of_work(doc,frm)
        set_raw_material(doc,frm)
        cur_frm.doc.item_code = doc.item_code
        cur_frm.doc.qty = doc.qty
        cur_frm.doc.rate = doc.rate
        cur_frm.doc.amount = doc.amount
        cur_frm.refresh_field("item_code")
        cur_frm.refresh_field("qty")
        cur_frm.refresh_field("rate")
        cur_frm.refresh_field("amount")
    set_property_finished_item_fields(frm,cur_frm)
    })
}
function set_property_finished_item_fields(frm, cur_frm) {
  frm.set_df_property('item_code', 'read_only', cur_frm.doc.item_code !== undefined);
  frm.set_df_property('qty', 'read_only', cur_frm.doc.qty > 0);
  frm.set_df_property('rate', 'read_only', cur_frm.doc.rate > 0);
  frm.set_df_property('amount', 'read_only', cur_frm.doc.amount > 0);
}
function set_scoop_of_work(doc, frm) {
    cur_frm.clear_table("scoop_of_work")
  for(var i =0;i<doc.scoop_of_work.length;i+=1){
      var row = doc.scoop_of_work[i]
      frm.add_child('scoop_of_work', {
            work_name: row.work_name,
            estimated_date: row.estimated_date,
            cost: row.cost,
            remarks: row.remarks
        });

    frm.refresh_field('scoop_of_work');
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
            qty: row.qty,
            rate: row.rate,
            amount: row.amount
        });

    frm.refresh_field('raw_material');
  }
}
