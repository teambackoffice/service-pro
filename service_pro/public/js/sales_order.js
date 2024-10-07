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
    custom_company_bank_details: function(frm) {
        if (frm.doc.custom_company_bank_details) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Company Bank Detailes',
                    name: frm.doc.custom_company_bank_details
                },
                callback: function(r) {
                    if (r.message) {
                        
                        let account_no = r.message.bank_account_no || '';
                        let iban_no = r.message.iban || '';
                        let bank_name = r.message.bank || '';

                        frm.set_value('custom_account_name', `Account No: ${account_no}\nIBAN: ${iban_no}\nBank Name: ${bank_name}`);
                    }
                }
            });
        } else {
            frm.set_value('custom_account_name', '');
        }
    },
});


