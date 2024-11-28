// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inter Company Stock Transfer Template", {
    refresh: function(frm) {
      
        frm.set_query('from_warehouse', function() {
            if (frm.doc.from_company) {
                return {
                    filters: {
                        company: frm.doc.from_company
                    }
                };
            }
        });

        frm.set_query('from_company_debit_account', function() {
            if (frm.doc.from_company) {
                return {
                    filters: {
                        company: frm.doc.from_company,
                        
                        is_group: 0
                    }
                };
            }
        });
        frm.set_query('from_cost_center', function() {
            if (frm.doc.from_company) {
                return {
                    filters: {
                        company: frm.doc.from_company,
                        
                    }
                };
            }
        });
        frm.set_query('to_warehouse', function() {
            if (frm.doc.to_company) {
                return {
                    filters: {
                        company: frm.doc.to_company
                    }
                };
            }
        });
        frm.set_query('to_company_credit_account', function() {
            if (frm.doc.to_company) {
                return {
                    filters: {
                        company: frm.doc.to_company,
                      
                        is_group: 0
                    }
                };
            }
        });
        frm.set_query('to_cost_center', function() {
            if (frm.doc.to_company) {
                return {
                    filters: {
                        company: frm.doc.to_company,
                        
                    }
                };
            }
        });

    }
});

