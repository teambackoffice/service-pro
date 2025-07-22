// Copyright (c) 2025, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inter Company Journal Entry", {
	refresh(frm) {
        frm.fields_dict['details'].grid.get_field('account').get_query = function(doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        'company': row.company,
                        'is_group': 0  
                    }
                };
            }
            return {};
        };

	},
});
