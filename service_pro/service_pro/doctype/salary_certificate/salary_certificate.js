// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Certificate", {
	company: function(frm) {
        if (frm.doc.company) {
            frm.set_query("employee", function() {
                return {
                    filters: {
                        company: frm.doc.company
                    }
                };
            });
        }
    },
    employee: function(frm) {
        if (frm.doc.employee) {
            // Call a server-side method to get passport and iqama numbers
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Employee",
                    name: frm.doc.employee
                },
                callback: function(r) {
                    if (r.message) {
                        // Set the fetched values in the form fields
                        frm.set_value("passport_no", r.message.passport_number);
                        frm.set_value("iqama_no", r.message.custom_iqama_number);
                        frm.set_value("employee_name",r.message.employee_name);
                        frm.set_value("designation",r.message.designation);
                    }
                }
            });
        }
    },
    // terms: function(frm) {
    //     if (frm.doc.terms) {
    //         frappe.call({
    //             method: 'frappe.client.get',
    //             args: {
    //                 doctype: 'Terms and Conditions',
    //                 name: frm.doc.terms,
    //             },
    //             callback: function(r) {console.log(r)
    //                 if (r.message) {
    //                     // Set the fetched template content in the Text Editor field
    //                     frm.set_value('template', r.message.terms_and_conditions_details);
    //                 } 
    //             }
    //         });
    //     } 
    // },
    terms: function (frm) {
		erpnext.utils.get_terms(frm.doc.terms, frm.doc, function (r) {
			if (!r.exc) {console.log(r.message)
				frm.set_value("template", r.message);
			}
		});
	},
    amount: function(frm){
        if (frm.doc.amount){
            frappe.call({
                method: "service_pro.service_pro.doctype.salary_certificate.salary_certificate.get_amount_in_words",
                args: {
                    amount : frm.doc.amount
                },
                callback: function(r) {
                    if (r.message) {
                        console.log("Amount in words:", r.message);
                        // Use r.message as needed, for example:
                        frm.set_value("amount_in_words", r.message);
                    }
                }
            });
                      
        }
    }
});
