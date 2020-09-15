// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Visit Report', {
	refresh: function(frm) {

	}
});

cur_frm.cscript.svrj_status = function (frm,cdt,cdn) {
    var row = locals[cdt][cdn]
    var job_card_number = frappe.meta.get_docfield("Site Visit Report Jobs", "job_card_number", cur_frm.doc.name);

    if(row.svrj_status === "For Visit"){
                job_card_number.fieldtype = "Data"

    } else if(row.svrj_status === "For Work"){
        console.log("FOR WORK")
                job_card_number.fieldtype = "Select"

    }
    cur_frm.refresh_field("site_visit_report_jobs")
}