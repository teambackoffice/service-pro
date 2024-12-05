frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
    if (frm.doc.docstatus == 1 && frm.doc.status != "To Bill") {
        frm.add_custom_button(__('Supplier Packing Slip'), function() {
            frappe.call({
                method: "service_pro.doc_events.purchase_order.make_supplier_packing_slip",
                args: {
                    purchase_order: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: "Supplier Packing Slip is Created",
                            indicator: 'green'
                        }, 5);
                        frappe.set_route('Form', 'Supplier Packing Slip', r.message);
                    }
                }
            });
        }, __('Create'));
    }
},
})


frappe.ui.form.on('Purchase Order Item', {
    request: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        reset_fields(cdt, cdn);

        if (row.request === 'Stock' && row.item_code) {
            fetch_available_qty(row, frm.doc.transaction_date);
        } else if (row.request === 'Sales Order' && row.sales_order) {
            fetch_sales_order_id(row);
        } else if (row.request === 'Material Request' && row.material_request) {
            fetch_material_request_id(row);
        } else if (row.request === 'Sales Order') {
            frappe.msgprint(__('There is no purchase order against sales order.'));
        }
    },
    sales_order: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.sales_order) {
            fetch_sales_order_id(row);
        }
    },
    material_request: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.material_request) {
            fetch_material_request_id(row);
        }
    },
    item_code: function (frm, cdt, cdn) {
        reset_fields(cdt, cdn);
    }
});

function reset_fields(cdt, cdn) {
    frappe.model.set_value(cdt, cdn, 'aval_qty', null);
    frappe.model.set_value(cdt, cdn, 'order_id', null);
    frappe.model.set_value(cdt, cdn, 'request_id', null);
}

function fetch_available_qty(row, transaction_date) {
    frappe.call({
        method: "service_pro.doc_events.purchase_order.get_available_qty",
        args: {
            item_code: row.item_code,
            warehouse: row.warehouse,
            posting_date: transaction_date || frappe.datetime.now_date()
        },
        callback: function (r) {
            if (r.message !== undefined) {
                const availableQty = r.message;

                frappe.model.set_value(row.doctype, row.name, 'aval_qty', availableQty);

                if (availableQty === 0) {
                    frappe.msgprint({
                        title: __('No Quantity Available'),
                        message: __('Not Qty Available This Item'),
                        indicator: 'red'
                    });
                }
            } 
        }
    });
}

function fetch_sales_order_id(row) {
    frappe.call({
        method: "service_pro.doc_events.purchase_order.get_sales_order_id",
        args: {
            sales_order: row.sales_order,
            item_code: row.item_code
        },
        callback: function (r) {
            if (r.message) {
                frappe.model.set_value(row.doctype, row.name, 'order_id', r.message);
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: __('There is no purchase order against sales order.'),
                    indicator: 'red'
                });
            }
        }
    });
}

function fetch_material_request_id(row) {
    frappe.call({
        method: "service_pro.doc_events.purchase_order.get_material_request_id",
        args: {
            material_request: row.material_request,
            item_code: row.item_code
        },
        callback: function (r) {
            if (r.message) {
                frappe.model.set_value(row.doctype, row.name, 'request_id', r.message);
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: __('There is no purchase order against material request.'),
                    indicator: 'red'
                });
            }
        }
    });
}

