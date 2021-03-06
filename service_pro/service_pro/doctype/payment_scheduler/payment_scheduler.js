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
            var child = locals[cdt][cdn];
            var filters = [
                ["status", "in", ["Overdue", "Unpaid"]]
            ]
            if (cur_frm.doc.type === "Supplier"){
                filters.push(["supplier", "=", child.name1])
            } else if (cur_frm.doc.type === "Agent"){
                filters.push(["sales_person", "=", child.name1])
            }
            return {
                filters: filters
            }
        }
    }


});

cur_frm.cscript.details_add = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
    if(cur_frm.doc.type === "Supplier"){
        d.name_link = "Supplier"
        d.doc_link = "Purchase Invoice"
        cur_frm.trigger("refresh")
    } else if(cur_frm.doc.type === "Expense Claim"){
        d.name_link = "Employee"
        d.doc_link = "Expense Claim"
        cur_frm.trigger("refresh")
    } else if(cur_frm.doc.type === "Agent"){
        d.name_link = "Sales Person"
        d.doc_link = "Sales Invoice"
        cur_frm.trigger("refresh")
    }
    cur_frm.refresh_field("details")
}
cur_frm.cscript.type = function (frm, cdt, cdn) {
    cur_frm.clear_table("details")
    cur_frm.refresh_field("details")

}

cur_frm.cscript.doc1 = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]
    if(row.doc1 && cur_frm.doc.type === "Supplier"){
        frappe.db.get_value('Purchase Invoice', row.doc1, 'outstanding_amount')
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
    } else if(row.doc1 && (cur_frm.doc.type === "Agent")) {
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
