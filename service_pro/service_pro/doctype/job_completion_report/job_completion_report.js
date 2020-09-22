// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Completion Report', {
	refresh: function(frm) {
        cur_frm.set_query('site_job_report', () => {
            return {
                filters: [
                    ["status", "=", "Completed"]
                ]
            }
        })
        cur_frm.set_query('production', () => {
            return {
                filters: [
                    ["status", "=", "Completed"]
                ]
            }
        })

    }
});
