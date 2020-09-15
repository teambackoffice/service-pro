// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Scheduler', {
	// refresh: function(frm) {

	// }
});


cur_frm.cscript.type = function () {
    console.log("JAJAJAJA")
    cur_frm.doc.name1 = ""
    cur_frm.refresh_field("name1")
    cur_frm.set_df_property("name1", "options", cur_frm.doc.type === "Supplier" ? cur_frm.doc.type : cur_frm.doc.type === "Expense Claim" ? "Employee" : "")
    if(cur_frm.doc.type === "Supplier" && cur_frm.doc.type === "Agent"){
        cur_frm.set_df_property("doc1", "options", "Sales Invoice")
        cur_frm.set_query('doc1', () => {
            return {
                filters: [
                    ["status", "in", ["Paid", "Unpaid"]]
                ]
            }
        })
        
    } else if (cur_frm.doc.type === "Expense Claim"){
                cur_frm.set_df_property("doc1", "options", "Expense Claim")
            cur_frm.set_query('doc1', () => {
                        return {
                            filters: [
                                ["employee", "=", cur_frm.doc.name1],
                                ["status", "in", ["Unpaid"]]
                            ]
                        }
                    })
    }

}

cur_frm.cscript.doc1 = function () {
    if(cur_frm.doc.doc1 && cur_frm.doc.type === "Supplier"){
        frappe.db.get_value('Sales Invoice', cur_frm.doc.doc1, 'outstanding_amount')
        .then(outstanding => {
            cur_frm.doc.outstanding = outstanding.message.outstanding_amount
            cur_frm.refresh_field("outstanding")
        })
    } else if(cur_frm.doc.doc1 && cur_frm.doc.type === "Expense Claim") {
        frappe.db.get_value('Expense Claim', cur_frm.doc.doc1, 'total_claimed_amount')
        .then(total_claimed_amount => {
            cur_frm.doc.outstanding = total_claimed_amount.message.total_claimed_amount
            cur_frm.refresh_field("outstanding")
        })
    } else if(cur_frm.doc.doc1 && cur_frm.doc.type === "Agent") {
        frappe.db.get_value('Sales Invoice', cur_frm.doc.doc1, 'incentive')
        .then(incentive => {
            cur_frm.doc.outstanding = incentive.message.incentive
            cur_frm.refresh_field("outstanding")
        })
    }
}
cur_frm.cscript.name1 = function () {
    if(cur_frm.doc.name1 && cur_frm.doc.type === "Expense Claim"){
        frappe.db.get_value('Employee', cur_frm.doc.name1, 'employee_name')
        .then(employee_name => {
            cur_frm.doc.employee_name = employee_name.message.employee_name
            cur_frm.refresh_field("employee_name")
        })
    }
}