frappe.ui.form.on("Inter Company Material Request", {
    schedule_date: function(frm) {
        if (frm.doc.schedule_date) {
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "schedule_date", frm.doc.schedule_date);
            });
        }
    },
    refresh: function(frm) {
        frm.set_query("company", function() {
            return {
                filters: {
                    is_group: 0  
                }
            };
        });
        
    },

    // Auto-populate table warehouses when set_warehouse is changed
    set_warehouse: function(frm) {
        if (frm.doc.set_warehouse) {
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "warehouse", frm.doc.set_warehouse);
            });
        }
    },

    // Auto-populate table from_warehouses when set_source_warehouse is changed
    set_source_warehouse: function(frm) {
        if (frm.doc.set_source_warehouse) {
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "from_warehouse", frm.doc.set_source_warehouse);
            });
        }
    },

    material_request_type: function(frm) {
        frm.doc.items.forEach(row => {
            if (row.stock_transfer_template) {
                frm.script_manager.trigger("stock_transfer_template", row.doctype, row.name);
            }
        });
    }
});

frappe.ui.form.on("Inter Company Material Request Item", {
    // Set up warehouse and from_warehouse filters when form loads or stock_transfer_template changes
    onload: function(frm, cdt, cdn) {
        setup_warehouse_filters(frm, cdt, cdn);
    },

    stock_transfer_template: function(frm, cdt, cdn) {
        let item = frappe.get_doc(cdt, cdn);
    
        // Setup filters first
        setup_warehouse_filters(frm, cdt, cdn);

        if (item.stock_transfer_template) {
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_available",
                args: {
                    item_code: item.item_code || "",  
                    stock_transfer_template: item.stock_transfer_template || "" 
                },
                callback: function(r) {
                    if (r.message || r.message === 0) {
                        frappe.model.set_value(cdt, cdn, "available_qty", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "available_qty", 0);
                    }
                }
            });

            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Inter Company Stock Transfer Template",
                    filters: {"name": item.stock_transfer_template},
                    fieldname: ["from_warehouse"]
                },
                callback: function(r) {
                    if (r.message && r.message.from_warehouse) {
                        if (frm.doc.material_request_type === "Material Transfer") {
                            frappe.model.set_value(cdt, cdn, "from_warehouse", r.message.from_warehouse);
                            frappe.model.set_value(cdt, cdn, "warehouse", "");
                        } else if (frm.doc.material_request_type === "Purchase") {
                            frappe.model.set_value(cdt, cdn, "warehouse", r.message.from_warehouse);
                            frappe.model.set_value(cdt, cdn, "from_warehouse", "");
                        }
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "available_qty", 0);
            frappe.model.set_value(cdt, cdn, "from_warehouse", "");
            frappe.model.set_value(cdt, cdn, "warehouse", "");
        }
    },

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
                        // Filter for non-HYDROTECH companies with qty > 0
                        let filtered_stock = r.message.filter(stock =>
                            (stock.company !== "HYDROTECH COMPANY CENTRAL WAREHOUSE" && stock.actual_qty > 0) ||
                            (stock.company === "HYDROTECH COMPANY CENTRAL WAREHOUSE") // Include HYDROTECH regardless of qty
                        );
    
                        if (filtered_stock.length > 0) {
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
    
                            filtered_stock.forEach(stock => {
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
                            // Check for "HYDROTECH COMPANY CENTRAL WAREHOUSE"
                            let hydro_stock = r.message.find(stock =>
                                stock.company === "HYDROTECH COMPANY CENTRAL WAREHOUSE"
                            );
    
                            if (hydro_stock) {
                                frm.fields_dict.stock_details.$wrapper.html(`
                                    <h5>Available Stock Details</h5>
                                    <table class="table table-bordered">
                                        <thead>
                                            <tr>
                                                <th>Company</th>
                                                <th>Item Code</th>
                                                <th>Item Name</th>
                                                <th>Warehouse</th>
                                                <th>Available Qty</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>${hydro_stock.company}</td>
                                                <td>${hydro_stock.item_code}</td>
                                                <td>${hydro_stock.item_name}</td>
                                                <td>${hydro_stock.warehouse}</td>
                                                <td>${hydro_stock.actual_qty}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                `);
                        } else {
                            frm.fields_dict.stock_details.$wrapper.empty();
                            frappe.msgprint({
                                title: __('No Stock Data'),
                                    message: __('No available stock for this item from valid companies or stock is zero.'),
                                indicator: 'red'
                            });
                            }
                        }
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
        
        // Clear rate when item changes and recalculate based on material request type
        frappe.model.set_value(cdt, cdn, "rate", 0);
        
        // Auto-calculate rate if warehouse/from_warehouse is already selected
        setTimeout(() => {
            let updated_item = frappe.get_doc(cdt, cdn);
            if (frm.doc.material_request_type === "Purchase" && updated_item.warehouse) {
                // Trigger warehouse calculation for Purchase type
                frm.script_manager.trigger("warehouse", cdt, cdn);
            } else if (frm.doc.material_request_type === "Material Transfer" && updated_item.from_warehouse) {
                // Trigger from_warehouse calculation for Material Transfer type
                frm.script_manager.trigger("from_warehouse", cdt, cdn);
            }
        }, 100);
    },

    // Warehouse field trigger for Purchase type
    warehouse: function(frm, cdt, cdn) {
        let item = frappe.get_doc(cdt, cdn);
        
        // Only trigger if material_request_type is "Purchase"
        if (frm.doc.material_request_type === "Purchase" && item.item_code && item.warehouse) {
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_warehouse_valuation_rate",
                args: {
                    item_code: item.item_code,
                    warehouse: item.warehouse
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "rate", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "rate", 0);
                        frappe.msgprint({
                            title: __('No Valuation Rate'),
                            message: __('No valuation rate found for item {0} in warehouse {1}', [item.item_code, item.warehouse]),
                            indicator: 'orange'
                        });
                    }
                }
            });
        } else if (frm.doc.material_request_type !== "Purchase") {
            frappe.model.set_value(cdt, cdn, "rate", 0);
        }
    },

    // From Warehouse field trigger for Material Transfer type
    from_warehouse: function(frm, cdt, cdn) {
        let item = frappe.get_doc(cdt, cdn);
        
        // Only trigger if material_request_type is "Material Transfer"
        if (frm.doc.material_request_type === "Material Transfer" && item.item_code && item.from_warehouse) {
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_material_request.inter_company_material_request.get_warehouse_valuation_rate",
                args: {
                    item_code: item.item_code,
                    warehouse: item.from_warehouse
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "rate", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "rate", 0);
                        frappe.msgprint({
                            title: __('No Valuation Rate'),
                            message: __('No valuation rate found for item {0} in from warehouse {1}', [item.item_code, item.from_warehouse]),
                            indicator: 'orange'
                        });
                    }
                }
            });
        } else if (frm.doc.material_request_type !== "Material Transfer") {
            frappe.model.set_value(cdt, cdn, "rate", 0);
        }
    },

    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Check if stock_transfer_template is selected and get from_company
        if (row.stock_transfer_template) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Inter Company Stock Transfer Template",
                    filters: {"name": row.stock_transfer_template},
                    fieldname: ["from_company"]
                },
                callback: function(r) {
                    if (r.message && r.message.from_company) {
                        // Only show validation error if NOT from HYDROTECH COMPANY CENTRAL WAREHOUSE
                        if (r.message.from_company !== "HYDROTECH COMPANY CENTRAL WAREHOUSE") {
                            if (row.qty > row.available_qty) {
                                frappe.msgprint(__('The Item requested quantity exceeds the available quantity.'));
                                frappe.model.set_value(cdt, cdn, 'qty', row.available_qty);
                            }
                        }
                        // If from HYDROTECH COMPANY CENTRAL WAREHOUSE, allow any quantity without validation
                    }
                }
            });
        } else {
            // If no template selected, apply default validation
            if (row.qty > row.available_qty) {
                frappe.msgprint(__('The Item requested quantity exceeds the available quantity.'));
                frappe.model.set_value(cdt, cdn, 'qty', row.available_qty);
            }
        }
    }
});

// Function to setup warehouse filters based on stock_transfer_template's from_company
function setup_warehouse_filters(frm, cdt, cdn) {
    let item = frappe.get_doc(cdt, cdn);
    
    if (item.stock_transfer_template) {
        // Get the from_company from the selected stock_transfer_template
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Inter Company Stock Transfer Template",
                filters: {"name": item.stock_transfer_template},
                fieldname: ["from_company"]
            },
            callback: function(r) {
                if (r.message && r.message.from_company) {
                    let from_company = r.message.from_company;
                    
                    // Set filter for warehouse field
                    frm.fields_dict.items.grid.get_field('warehouse').get_query = function(doc, cdt, cdn) {
                        return {
                            filters: {
                                company: from_company
                            }
                        };
                    };
                    
                    // Set filter for from_warehouse field
                    frm.fields_dict.items.grid.get_field('from_warehouse').get_query = function(doc, cdt, cdn) {
                        return {
                            filters: {
                                company: from_company
                            }
                        };
                    };
                    
                    // Refresh the grid to apply filters
                    frm.refresh_field("items");
                }
            }
        });
    } else {
        // Clear filters if no stock_transfer_template is selected
        frm.fields_dict.items.grid.get_field('warehouse').get_query = null;
        frm.fields_dict.items.grid.get_field('from_warehouse').get_query = null;
        frm.refresh_field("items");
    }
}