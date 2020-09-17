// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Visit Report', {
	refresh: function(frm) {
        document.querySelectorAll("[data-doctype='Site Job Report']")[1].style.display ="none";
	}
});

cur_frm.cscript.generate_site_job_report = function (frm,cdt,cdn) {
        var row = locals[cdt][cdn]
        frappe.call({
          method: "service_pro.service_pro.doctype.site_visit_report.site_visit_report.generate_sjr",
            args: {
              name: row.name,
            },
            callback: function () {
              cur_frm.reload_doc()
            }
        })

}