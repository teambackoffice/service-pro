frappe.ui.form.on('Customer', {
    tax_id: function(frm) {
        if (frm.doc.tax_id) {
            frm.set_value('custom_vat_registration_number', frm.doc.tax_id);
        }
    }
});
