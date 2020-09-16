// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Visit Report', {
	refresh: function(frm) {

	}
});

cur_frm.cscript.svrj_status = function (frm,cdt,cdn) {
    var row = locals[cdt][cdn]
    console.log(row.svrj_status !== "Troubleshooting")

    var job_card_number = frappe.meta.get_docfield("Site Visit Report Jobs", "job_card_number", cur_frm.doc.name);
     job_card_number.read_only = row.svrj_status  !== "Troubleshooting"
        cur_frm.refresh_field("site_visit_report_jobs")

}
cur_frm.cscript.site_visit_report_jobs_add = function (frm,cdt,cdn) {
        var row = locals[cdt][cdn]
console.log(row.svrj_status !== "Troubleshooting")
    var job_card_number = frappe.meta.get_docfield("Site Visit Report Jobs", "job_card_number", cur_frm.doc.name);

     job_card_number.read_only = row.svrj_status !== "Troubleshooting"
        cur_frm.refresh_field("site_visit_report_jobs")

}