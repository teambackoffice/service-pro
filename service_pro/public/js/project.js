frappe.ui.form.on('Project', {
    refresh: function (frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Service Receipt Note'), function () {
                frappe.new_doc('Service Receipt Note', {
                    project_id: frm.doc.project_id, 
                    project: frm.doc.name, 
                    customer: frm.doc.customer
                });
            }, __('Create')); 
        }
    },
});

