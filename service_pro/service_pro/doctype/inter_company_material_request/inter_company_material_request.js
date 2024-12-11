frappe.ui.form.on("Inter Company Material Request", {
    validate: function(frm) {
        let has_insufficient_stock = false;

        frm.doc.items.forEach(item => {
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_available_qty",
                args: {
                    item_code: item.item_code
                },
                async: false,
                callback: function(r) {
                    if (r.message && r.message.some(stock => stock.actual_qty === 0)) {
                        has_insufficient_stock = true;
                        frappe.msgprint({
                            title: __('Validation Error'),
                            message: __('Cannot save. Insufficient stock for {0} - {1}.', [item.item_name, item.item_code]),
                            indicator: 'red'
                        });
                    }
                }
            });

            if (has_insufficient_stock) {
                frappe.validated = false;
                return false; 
            }
        });
    },
    schedule_date: function(frm) {
        if (frm.doc.schedule_date) {
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "schedule_date", frm.doc.schedule_date);
            });
        }
    },
    refresh: function(frm) {
        // frm.fields_dict.stock_details.$wrapper.empty();
        // frm.fields_dict["items"].grid.get_field("supplier").get_query = function(doc, cdt, cdn) {
        //     return {
        //         filters: {
        //             is_internal_supplier: 1
        //         }
        //     };
        // };

        frm.set_query("set_warehouse", function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        company: frm.doc.company,
                        is_group: 0
                    }
                };
            }
        });
        frm.set_query("company", function() {
            return {
                filters: {
                    is_group: 0  
                }
            };
        });
        
    }
});

frappe.ui.form.on("Inter Company Material Request Item", {
    item_code: function(frm, cdt, cdn) {
        let item = frappe.get_doc(cdt, cdn);

        if (item.item_code) {
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_available_qty",
                args: {
                    item_code: item.item_code
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let html_content = `<h5>Available Stock Details</h5>`;
                        html_content += `<table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Company</th>
                                    <th>Item Code</th>
                                    <th>Item Name</th>
                                    <th>Warehouse</th>
                                    <th>Available Qty</th>
                                </tr>
                            </thead>
                            <tbody>`;

                        r.message.forEach(stock => {
                            html_content += `<tr>
                                <td>${stock.company}</td>
                                <td>${stock.item_code}</td>
                                <td>${stock.item_name}</td>
                                <td>${stock.warehouse}</td>
                                <td>${stock.actual_qty}</td>
                            </tr>`;
                        });

                        html_content += `</tbody></table>`;

                        frm.fields_dict.stock_details.$wrapper.html(html_content);
                    } else {
                        frappe.call({
                            method: "frappe.client.get",
                            args: {
                                doctype: "Item",
                                name: item.item_code
                            },
                            callback: function(r) {
                                let item_name = r.message?.item_name || "Unknown Item";

                                frm.fields_dict.stock_details.$wrapper.empty();
                                frappe.msgprint({
                                    title: __('No Stock Data'),
                                    message: __("Insufficient Stock for {0} - {1}", [item_name, item.item_code]),
                                    indicator: 'red'
                                });

                                frappe.model.clear_doc(cdt, cdn);
                                frm.refresh_field("items");
                            }
                        });
                    }
                }
            });

            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Item",
                    name: item.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
                        frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                    }
                }
            });
        } else {
            frm.fields_dict.stock_details.$wrapper.empty();
        }
    },

    stock_transfer_template: function(frm, cdt, cdn) {
        let item = frappe.get_doc(cdt, cdn);
        if (item.stock_transfer_template){

        }
        frappe.call({
            method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_available",
            args: {
                item_code: item.item_code,
                stock_transfer_template : item.stock_transfer_template

            },
            callback: function(r) {console.log(r)
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "available_qty", r.message);
                    
                }
            }
        });

    },
    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.qty > row.available_qty) {
            frappe.msgprint(__('The Item requested quantity exceeds the available quantity.'));
            frappe.model.set_value(cdt, cdn, 'qty', row.available_qty);
        }
    }
});