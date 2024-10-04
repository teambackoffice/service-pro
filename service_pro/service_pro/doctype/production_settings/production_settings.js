// // Copyright (c) 2020, jan and contributors
// // For license information, please see license.txt

frappe.ui.form.on('Production Settings', {
    refresh: function(frm) {
        frm.fields_dict['finish_good_defaults'].grid.get_field('income_account').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['finish_good_defaults'].grid.get_field('finish_good_warehouse').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['finish_good_defaults'].grid.get_field('finish_good_cost_center').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['raw_material_defaults'].grid.get_field('warehouse').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['raw_material_defaults'].grid.get_field('cost_center').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['site_job_report_settings'].grid.get_field('warehouse').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
        frm.fields_dict['site_job_report_settings'].grid.get_field('cost_center').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.company) {
                return {
                    filters: {
                        company: row.company
                    }
                };
            }
        };
    }
});
