// For Sales Order
frappe.ui.form.on('Sales Order', {
    onload: function(frm) {
        load_session_defaults(frm);
    }
});

// For Purchase Invoice
frappe.ui.form.on('Purchase Order', {
    onload: function(frm) {
        load_session_defaults(frm);
    }
});

frappe.ui.form.on('Delivery Note', {
    onload: function(frm) {
        load_session_defaults(frm);
    }
});

function load_session_defaults(frm) {
    if (!frm.doc) return;

    frappe.call({
        method: 'service_pro.service_pro.doctype.defaults_session_settings.defaults_session_settings.get_session_default_values',
        args: {
            doctype_type: frm.doctype
        },
        callback: function(r) {
            console.log("Loaded defaults for", frm.doctype, r.message);
            if (r.message) {
                if (r.message.company) frm.set_value('company', r.message.company);
                if (r.message.cost_center) frm.set_value('cost_center', r.message.cost_center);
                if (r.message.set_warehouse) frm.set_value('set_warehouse', r.message.set_warehouse);
            }
        }
    });
}