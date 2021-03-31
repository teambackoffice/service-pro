

cur_frm.cscript.salary_component = function () {
    if(cur_frm.doc.salary_component){
        frappe.db.get_doc('Salary Component', cur_frm.doc.salary_component)
            .then(sc => {
                cur_frm.doc.is_hour_based = sc.is_hour_based
                cur_frm.refresh_field("is_hour_based")
                cur_frm.set_df_property("amount", "reqd", !cur_frm.doc.is_hour_based)
                cur_frm.set_df_property("amount", "read_only", cur_frm.doc.is_hour_based)
                cur_frm.set_df_property("total_working_hour", "hidden", !cur_frm.doc.is_hour_based)
                 compute_total_working_hrs(cur_frm)
            })
    }
}
cur_frm.cscript.total_working_hour = function () {
    compute_total_working_hrs(cur_frm)
}
function compute_total_working_hrs(cur_frm) {

    if(cur_frm.doc.is_hour_based && cur_frm.doc.employee && cur_frm.doc.total_working_hour > 0){
        console.log("NAA MAAAAN")
        frappe.call({
            method: "service_pro.doc_events.additional_salary.get_salary_structure",
            args: {
                employee: cur_frm.doc.employee,
                total_working_hours: cur_frm.doc.total_working_hour ? cur_frm.doc.total_working_hour : 0
            },
            callback: function (r) {
                console.log("MESSAGE")
                console.log(r.message)
                    cur_frm.doc.amount = r.message
                    cur_frm.refresh_field("amount")

            }
        })
    } else {
        cur_frm.doc.amount = 0
        cur_frm.doc.total_working_hour = 0
        cur_frm.refresh_field("amount")
        cur_frm.refresh_field("total_working_hour")

    }


}