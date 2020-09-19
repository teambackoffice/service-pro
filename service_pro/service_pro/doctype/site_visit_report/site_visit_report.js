// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Visit Report', {
	refresh: function(frm) {
	    if(!cur_frm.is_new()){
            document.querySelectorAll("[data-doctype='Site Job Report']")[1].style.display ="none";

        }

         frm.fields_dict['site_visit_report_jobs'].grid.get_field('job_card_number').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            if(child.rework && child.svrj_status === "Troubleshooting"){
                console.log("test")
                return{
                    filters:[
                        ['status', '=', "In Progress"],
                        ['docstatus', '=', 1],
                        ['customer', '=', child.customer],

                    ]
                }
            } else {
                return{
                    filters:[]
                }
            }
        }
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
cur_frm.cscript.rework = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]
    if(row.rework && row.svrj_status === "Troubleshooting"){
            cur_frm.trigger("refresh")

    }
}
cur_frm.cscript.svrj_status = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn]
    if(row.rework && row.svrj_status === "Troubleshooting"){
            cur_frm.trigger("refresh")

    }
}
