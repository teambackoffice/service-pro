frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        frm.add_custom_button(
            __("Service Order Form"),
            function() {
                frappe.model.with_doctype('Service Order Form', function() {
                    var so_doc = frappe.model.get_new_doc('Service Order Form');

                    
                    so_doc.customer = frm.doc.customer; 
                    so_doc.currency = frm.doc.currency; 
                    so_doc.transaction_date = frm.doc.posting_date; 

                   
                    frappe.set_route('Form', 'Service Order Form', so_doc.name);
                });
            },
            __("Get Items From")
        );
    },
});


