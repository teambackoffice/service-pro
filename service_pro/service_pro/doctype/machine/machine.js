// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt
frappe.ui.form.on("Machine", {
    refresh(frm) {
        frm.set_query('company', function() {
            return {
                filters: {
                    name: frm.doc.company // Use 'name' instead of 'company'
                }
            };
        });
    },
});
