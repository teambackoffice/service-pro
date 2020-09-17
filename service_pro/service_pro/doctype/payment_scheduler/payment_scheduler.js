// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Scheduler','refresh', function(frm) {
    if(cur_frm.doc.type === "Expense Claim"){
        frm.fields_dict['details'].grid.get_field('doc1').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
			return{
                filters:[
                    ['employee', '=', child.name1],
                    ['status', '=', "Unpaid"],
                ]
            }
        }
    } else if (cur_frm.doc.type === "Supplier" || cur_frm.doc.type === "Agent") {
        frm.fields_dict['details'].grid.get_field("doc1").get_query = function (doc, cdt, cdn) {
            return {
                filters: [
                    ["status", "in", ["Paid", "Unpaid"]]
                ]
            }
        }
    }


});


cur_frm.cscript.type = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]

    cur_frm.clear_table("details")
    cur_frm.refresh_field("details")
    var name1 = frappe.meta.get_docfield("Payment Scheduler Details", "name1", cur_frm.doc.name);
    var doc1 = frappe.meta.get_docfield("Payment Scheduler Details", "doc1", cur_frm.doc.name);
    name1.options = cur_frm.doc.type === "Supplier" ? cur_frm.doc.type : cur_frm.doc.type === "Expense Claim" ? "Employee" : "Sales Person"

    if(cur_frm.doc.type === "Supplier" || cur_frm.doc.type === "Agent"){
        doc1.options = "Sales Invoice"
                cur_frm.trigger("refresh")


    } else if (cur_frm.doc.type === "Expense Claim"){
        doc1.options = "Expense Claim"
        cur_frm.trigger("refresh")
    }

}

cur_frm.cscript.doc1 = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]
    if(row.doc1 && cur_frm.doc.type === "Supplier"){
        frappe.db.get_value('Sales Invoice', row.doc1, 'outstanding_amount')
        .then(outstanding => {
            row.outstanding = outstanding.message.outstanding_amount
            cur_frm.refresh_field("details")
        })
    } else if(row.doc1 && cur_frm.doc.type === "Expense Claim") {
        frappe.db.get_value('Expense Claim', row.doc1, 'total_claimed_amount')
        .then(total_claimed_amount => {
            row.outstanding = total_claimed_amount.message.total_claimed_amount
            cur_frm.refresh_field("details")
        })
    } else if(row.doc1 && cur_frm.doc.type === "Agent") {
        frappe.db.get_value('Sales Invoice', row.doc1, 'incentive')
        .then(incentive => {
            row.outstanding = incentive.message.incentive
            cur_frm.refresh_field("details")
        })
    }
}
cur_frm.cscript.name1 = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]
    if(row.name1 && cur_frm.doc.type === "Expense Claim"){

        frappe.db.get_value('Employee', row.name1, 'employee_name')
        .then(employee_name => {
            row.employee_name = employee_name.message.employee_name
            cur_frm.refresh_field("details")
        })


    } else if(row.name1 && cur_frm.doc.type === "Supplier"){

        frappe.db.get_value('Supplier', row.name1, 'supplier_name')
        .then(supplier_name => {
            row.supplier_name = supplier_name.message.supplier_name
            cur_frm.refresh_field("details")
        })


    }

}
