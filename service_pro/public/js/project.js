frappe.ui.form.on('Project', {
    refresh: function (frm) {
        if (!frm.doc.__islocal) {
            frm.clear_custom_buttons();

            frm.add_custom_button(__('Service Receipt Note'), function () {
                frappe.new_doc('Service Receipt Note', {
                    project_id: frm.doc.project_id,
                    project: frm.doc.name,
                    customer: frm.doc.customer,
                    company: frm.doc.company
                });
            }, __('Create'));
        }
    },
    customer: function(frm) {
        if (frm.doc.customer) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Customer',
                    fieldname: 'customer_name',
                    filters: { name: frm.doc.customer }
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('custom_customer_name', r.message.customer_name);
                    }
                }
            });
        } else {
            frm.set_value('customer_name', '');
        }
    }
});



