frappe.ui.form.on('Inter Company Transfer', {
    company_name(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.company_name) {
            frappe.call({
                method: "service_pro.doc_events.delivery_trip.get_billing_address_by_title",  // replace with your actual path
                args: {
                    company_name: row.company_name
                },
                callback: function(r) {
                    if (r.message) {
                        // Replace <br> tags with newlines for clean display in text field
                        const clean_address = r.message.replace(/<br\s*\/?>/gi, "\n");
                        frappe.model.set_value(cdt, cdn, "address", clean_address);
                    } else {
                        frappe.model.set_value(cdt, cdn, "address", "");
                        frappe.msgprint("No address found for " + row.company_name);
                    }
                }
            });
        }
    }
});
