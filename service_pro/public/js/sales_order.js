frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        frm.add_custom_button(
            __("Service Order Form"), 
            function() {
                frappe.new_doc('Service Order Form');
            },
            __("Get Items From") 
        );
    }
});
