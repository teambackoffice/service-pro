frappe.ui.form.on('Defaults Session Settings', {
    onload: function(frm) {
        frm.fields_dict['defaults'].grid.get_field('cost_center').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.company
                }
            };
        };
        frm.fields_dict['defaults'].grid.get_field('set_warehouse').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.company
                }
            };
        };
    }
});
