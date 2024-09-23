frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        
            // Add Service Order Form button
            frm.add_custom_button(
                __("Service Order Form"),
                function() {
                    frappe.model.open_mapped_doc({
                        method: "service_pro.doc_events.sales_order.make_sales_order_from_service_order",
                        frm: frm
                    });
                },
                __("Get Items From")
            );
            
        }
    
});
