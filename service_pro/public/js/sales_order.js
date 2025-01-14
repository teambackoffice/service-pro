frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // Set query for the warehouse field
        frm.set_query('set_warehouse', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        company: frm.doc.company,
                        is_group: 0,
                    }
                };
            }
        });

        // Add custom button under the "Get Items From" section
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

        // Add custom button under the "Create" section
        frm.page.add_inner_button(
            __("Production"),
            function() {
                frappe.model.with_doctype('Production', function() {
                    var prod_doc = frappe.model.get_new_doc('Production');
        
                    // Set main fields
                    prod_doc.sales_order = frm.doc.name;
                    prod_doc.customer = frm.doc.customer;
                    prod_doc.company = frm.doc.company;
        
                    // Copy values from Sales Order Items table to Raw Material table in Production
                    $.each(frm.doc.items || [], function(index, item) {
                        var child_row = frappe.model.add_child(prod_doc, 'Raw Material', 'raw_material'); // Update with your actual child table fieldname
        
                        // Set values from Sales Order item to Production Raw Material row
                        child_row.item_code = item.item_code;
                        child_row.item_name = item.item_name;
                        child_row.quantity = item.qty;
                        child_row.uom = item.uom;
                        child_row.rate_raw_material = item.rate;
                        child_row.amount_raw_material = item.amount ;
                    });
        
                    // Navigate to the new Production form
                    frappe.set_route('Form', 'Production', prod_doc.name);
                });
            },
            __("Create")
        );
        
    },
    onload : function(frm) {
        frappe.call({
            method: "service_pro.doc_events.sales_order.get_role",
            callback: function (r) {
                if (r.message) {
                    const authorized_role = r.message; 
                    console.log("Authorized Role:", authorized_role);
        
                    if (frappe.user_roles.includes(authorized_role)) {
                        frm.set_df_property('custom_ignore_permission_', 'read_only', 0); 
                        frm.set_value('custom_ignore_permission_', 1); 
                    } else {
                        frm.set_df_property('custom_ignore_permission_', 'read_only', 1); 
                        frm.set_value('custom_ignore_permission_', 0); 
                    }
                } else {
                    console.error("No authorized role found.");
                }
            }
        });
    },
});
