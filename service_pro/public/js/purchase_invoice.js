// Copyright (c) 2024, D-codE and contributors
// For license information, please see license.txt


frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        frappe.db.get_single_value("Production Settings", "debit_note_user_role").then((value) => {
            if(value) {
                if (!frappe.user_roles.includes(value)) {
                    frm.toggle_display("is_return", false)
                    setTimeout(() => {
                        frm.remove_custom_button('Return / Debit Note', "Create");
                    }, 500);
                }
            }                           
        }); 
        if( frm.doc.items[0].purchase_order){
            frm.get_field('items').grid.cannot_add_rows = true;
        }else{
            frm.get_field('items').grid.cannot_add_rows = false;

        }
    },
    
});