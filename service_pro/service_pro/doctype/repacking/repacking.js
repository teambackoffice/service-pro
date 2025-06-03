// Copyright (c) 2025, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repacking', {
    onload: function(frm) {
        // Setup batch_no filter for repack_item child table
        if (frm.fields_dict["repack_item"]) {
            frm.fields_dict["repack_item"].grid.get_field("batch_no").get_query = function(doc, cdt, cdn) {
                let row = locals[cdt][cdn];
                if (row && row.item_code) {
                    let filters = {
                        "item_code": row.item_code
                    };
                    
                    // Add warehouse filter if warehouse is selected
                    if (row.warehouse) {
                        filters["warehouse"] = row.warehouse;
                    }
                    
                    return {
                        query: "erpnext.controllers.queries.get_batch_no",
                        filters: filters
                    };
                }
                return {
                    filters: {
                        "name": ["=", ""]  // Return empty if no item selected
                    }
                };
            };
        }
    },

    setup: function(frm) {
        // Set up warehouse queries
        frm.set_query('source_warehouse', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        'company': frm.doc.company,
                        'is_group': 0
                    }
                };
            } else {
                frappe.msgprint(__('Please select a Company first'));
                return {
                    filters: {
                        'name': 'No Company Selected'
                    }
                };
            }
        });

        frm.set_query('target_warehouse', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        'company': frm.doc.company,
                        'is_group': 0
                    }
                };
            } else {
                frappe.msgprint(__('Please select a Company first'));
                return {
                    filters: {
                        'name': 'No Company Selected'
                    }
                };
            }
        });

        // Set up cost center query based on company
        frm.set_query('cost_center', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        'company': frm.doc.company,
                        'is_group': 0,
                        'disabled': 0
                    }
                };
            } else {
                frappe.msgprint(__('Please select a Company first'));
                return {
                    filters: {
                        'name': 'No Company Selected'
                    }
                };
            }
        });

        frm.set_query('warehouse', 'repack_item', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        'company': frm.doc.company,
                        'is_group': 0
                    }
                };
            } else {
                frappe.msgprint(__('Please select a Company first'));
                return {
                    filters: {
                        'name': 'No Company Selected'
                    }
                };
            }
        });

        frm.set_query('warehouse', 'target_item', function() {
            if (frm.doc.company) {
                return {
                    filters: {
                        'company': frm.doc.company,
                        'is_group': 0
                    }
                };
            } else {
                frappe.msgprint(__('Please select a Company first'));
                return {
                    filters: {
                        'name': 'No Company Selected'
                    }
                };
            }
        });

        // Set up item query for repack_item table
        frm.set_query('item_code', 'repack_item', function() {
            return {
                filters: {
                    'is_stock_item': 1,
                    'disabled': 0
                }
            };
        });
    },

    refresh: function(frm) {
        // Add custom button for generating items
        if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Generate Items'), function() {
                frm.events.generate_item(frm);
            }, __('Actions'));
        }

    },
    on_update: function(frm) {
        // Calculate totals on update
        frm.events.calculate_outgoing_total(frm);
        frm.events.calculate_incoming_total(frm);
        frm.events.calculate_difference_value(frm);
    },

    // Function to calculate total outgoing value from repack_item table
    calculate_outgoing_total: function(frm) {
        let total_outgoing = 0;
        
        if (frm.doc.repack_item && frm.doc.repack_item.length > 0) {
            frm.doc.repack_item.forEach(function(row) {
                if (row.valuation_rate && row.qty) {
                    total_outgoing += (row.valuation_rate * row.qty);
                } else if (row.valuation_rate && !row.qty) {
                    // If no qty field, just sum the valuation rates
                    total_outgoing += row.valuation_rate;
                }
            });
        }
        
        frm.set_value('total_outgoing_value', total_outgoing);
        // Trigger difference calculation after outgoing total update
        frm.events.calculate_difference_value(frm);
    },

    // Function to calculate total incoming value from target_item table using amount field
    calculate_incoming_total: function(frm) {
        let total_incoming = 0;
        
        if (frm.doc.target_item && frm.doc.target_item.length > 0) {
            frm.doc.target_item.forEach(function(row) {
                // Use amount field if available, otherwise fallback to qty * valuation_rate
                if (row.amount) {
                    total_incoming += row.amount;
                } else if (row.valuation_rate && row.qty) {
                    total_incoming += (row.valuation_rate * row.qty);
                } else if (row.valuation_rate && !row.qty) {
                    // If no qty field, just sum the valuation rates
                    total_incoming += row.valuation_rate;
                }
            });
        }
        
        frm.set_value('total_incoming_value', total_incoming);
        // Trigger difference calculation after incoming total update
        frm.events.calculate_difference_value(frm);
    },

    // Function to calculate difference value (total_outgoing_value - total_incoming_value)
    calculate_difference_value: function(frm) {
        let total_outgoing = frm.doc.total_outgoing_value || 0;
        let total_incoming = frm.doc.total_incoming_value || 0;
        let difference = total_outgoing - total_incoming;
        
        frm.set_value('total_difference_value', difference);
    },

    // Event handlers for when total values change directly
    total_outgoing_value: function(frm) {
        frm.events.calculate_difference_value(frm);
    },

    total_incoming_value: function(frm) {
        frm.events.calculate_difference_value(frm);
    },

    company: function(frm) {
        // Clear cost center when company changes
        if (frm.doc.cost_center) {
            frm.set_value('cost_center', '');
            frappe.show_alert({
                message: __('Cost Center cleared due to Company change'),
                indicator: 'orange'
            });
        }

        if (frm.doc.source_warehouse) {
            frm.set_value('source_warehouse', '');
            frappe.show_alert({
                message: __('Source Warehouse cleared due to Company change'),
                indicator: 'orange'
            });
        }

        if (frm.doc.target_warehouse) {
            frm.set_value('target_warehouse', '');
            frappe.show_alert({
                message: __('Target Warehouse cleared due to Company change'),
                indicator: 'orange'
            });
        }

        frm.refresh_field('cost_center');
        frm.refresh_field('source_warehouse');
        frm.refresh_field('target_warehouse');

        if (frm.doc.repack_item && frm.doc.repack_item.length > 0) {
            frm.doc.repack_item.forEach(function(row) {
                if (row.warehouse) {
                    frappe.model.set_value(row.doctype, row.name, 'warehouse', '');
                }
            });
            frm.refresh_field('repack_item');
        }

        if (frm.doc.target_item && frm.doc.target_item.length > 0) {
            frm.doc.target_item.forEach(function(row) {
                if (row.warehouse) {
                    frappe.model.set_value(row.doctype, row.name, 'warehouse', '');
                }
            });
            frm.refresh_field('target_item');
        }
    },

    source_warehouse: function(frm) {
        if (frm.doc.source_warehouse && frm.doc.repack_item) {
            frm.doc.repack_item.forEach(function(row) {
                frappe.model.set_value(row.doctype, row.name, 'warehouse', frm.doc.source_warehouse);
            });
            frm.refresh_field('repack_item');
        }
    },

    target_warehouse: function(frm) {
        if (frm.doc.target_warehouse && frm.doc.target_item) {
            frm.doc.target_item.forEach(function(row) {
                frappe.model.set_value(row.doctype, row.name, 'warehouse', frm.doc.target_warehouse);
            });
            frm.refresh_field('target_item');

            frappe.show_alert({
                message: __('Warehouse updated in all target items'),
                indicator: 'green'
            });
        }
    },

    // Optimized Generate Item functionality
    generate_item: function(frm) {
        // Validate if target_item table has data
        if (!frm.doc.target_item || frm.doc.target_item.length === 0) {
            frappe.msgprint({
                title: __('No Target Items'),
                message: __('Please add target items before generating'),
                indicator: 'red'
            });
            return;
        }

        // Check if all target items have item_name and uom
        let incomplete_items = [];
        let items_to_generate = [];
        
        frm.doc.target_item.forEach(function(row) {
            if (!row.target_item_code) {  // Only check rows without item codes
                if (!row.item_name || !row.uom) {
                    incomplete_items.push(row.idx);
                } else {
                    items_to_generate.push(row);
                }
            }
        });

        if (incomplete_items.length > 0) {
            frappe.msgprint({
                title: __('Incomplete Data'),
                message: __('Please fill Item Name and UOM for rows: {0}', [incomplete_items.join(', ')]),
                indicator: 'orange'
            });
            return;
        }

        if (items_to_generate.length === 0) {
            frappe.msgprint({
                title: __('No Items to Generate'),
                message: __('All target items already have item codes generated'),
                indicator: 'blue'
            });
            return;
        }

        // Optimized item generation - only update specific fields
        frm.call({
            doc: frm.doc,
            method: "generate_items",
            freeze: true,
            freeze_message: __("Generating Items..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    // Update only the target_item_code fields in the form
                    if (r.message.generated_items) {
                        r.message.generated_items.forEach(function(generated_item) {
                            // Find the corresponding row and update target_item_code
                            frm.doc.target_item.forEach(function(target_row) {
                                if (target_row.item_name === generated_item.item_name && 
                                    target_row.uom === generated_item.uom && 
                                    target_row.idx === generated_item.row &&
                                    !target_row.target_item_code) {
                                    
                                    // Update the field in the form
                                    target_row.target_item_code = generated_item.item_code;
                                }
                            });
                        });
                        
                        // Refresh only the target_item table
                        frm.refresh_field('target_item');
                    }
                } else {
                    frappe.msgprint({
                        title: __('Generation Status'),
                        message: r.message.message || __('No items were generated'),
                        indicator: 'blue'
                    });
                }
            },
            error: function(r) {
                frappe.msgprint({
                    title: __('Generation Failed'),
                    message: __('An error occurred while generating items. Please check the error log.'),
                    indicator: 'red'
                });
                console.error('Item generation error:', r);
            }
        });
    }
});

// Enhanced Target Item table events with amount calculation
frappe.ui.form.on('Target Item', {
    target_item_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (frm.doc.target_warehouse) {
            frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.target_warehouse);
        }
    },

    item_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Clear the target_item_code if item_name is changed
        if (row.target_item_code && row.item_name) {
            frappe.model.set_value(cdt, cdn, 'target_item_code', '');
            frappe.show_alert({
                message: __('Target Item Code cleared due to Item Name change'),
                indicator: 'orange'
            });
        }
    },

    uom: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Clear the target_item_code if UOM is changed
        if (row.target_item_code && row.uom) {
            frappe.model.set_value(cdt, cdn, 'target_item_code', '');
            frappe.show_alert({
                message: __('Target Item Code cleared due to UOM change'),
                indicator: 'orange'
            });
        }
    },

    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && row.warehouse) {
            get_bin_data(frm, cdt, cdn, row.item_code, row.warehouse);
        }
    },

    warehouse: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && row.warehouse) {
            get_bin_data(frm, cdt, cdn, row.item_code, row.warehouse);
        }
    },

    // Calculate amount when qty changes
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        frm.events.calculate_incoming_total(frm);
    },

    // Calculate amount when valuation_rate changes
    valuation_rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        frm.events.calculate_incoming_total(frm);
    },

    // Recalculate incoming total when amount changes directly
    amount: function(frm, cdt, cdn) {
        frm.events.calculate_incoming_total(frm);
    },

    target_item_remove: function(frm, cdt, cdn) {
        frm.refresh_field('target_item');
        // Recalculate total after removing row
        setTimeout(() => {
            frm.events.calculate_incoming_total(frm);
        }, 100);
    }
});

// Enhanced Repack Item table events with batch functionality
frappe.ui.form.on('Repack Item', {
    repack_item_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (frm.doc.source_warehouse) {
            frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.source_warehouse);
        }
    },

    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.item_code) {
            // Clear batch when item changes
            if (row.batch_no) {
                frappe.model.set_value(cdt, cdn, 'batch_no', '');
                frappe.show_alert({
                    message: __('Batch cleared due to Item change'),
                    indicator: 'orange'
                });
            }

            // Get item details including UOM
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Item',
                    name: row.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        let item = r.message;
                        
                        // Set UOM from item's stock UOM
                        if (item.stock_uom) {
                            frappe.model.set_value(cdt, cdn, 'uom', item.stock_uom);
                        }
                        
                        // Get bin data if warehouse is selected
                        if (row.warehouse) {
                            get_bin_data(frm, cdt, cdn, row.item_code, row.warehouse);
                        }
                        
                        // Refresh the batch field filter
                        frm.fields_dict["repack_item"].grid.grid_rows_by_docname[cdn].refresh_field("batch_no");
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Error fetching item details'),
                        indicator: 'red'
                    });
                    console.error('Error fetching item details:', r);
                }
            });
        } else {
            // Clear dependent fields when item is cleared
            frappe.model.set_value(cdt, cdn, 'uom', '');
            frappe.model.set_value(cdt, cdn, 'valuation_rate', 0);
            frappe.model.set_value(cdt, cdn, 'avail_qty', 0);
            frappe.model.set_value(cdt, cdn, 'batch_no', '');
        }
    },

    warehouse: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Clear batch when warehouse changes
        if (row.batch_no) {
            frappe.model.set_value(cdt, cdn, 'batch_no', '');
            frappe.show_alert({
                message: __('Batch cleared due to Warehouse change'),
                indicator: 'orange'
            });
        }
        
        if (row.item_code && row.warehouse) {
            get_bin_data(frm, cdt, cdn, row.item_code, row.warehouse);
        }
        
        // Refresh the batch field filter
        if (row.item_code) {
            frm.fields_dict["repack_item"].grid.grid_rows_by_docname[cdn].refresh_field("batch_no");
        }
    },

    batch_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.batch_no && row.item_code && row.warehouse) {
            // Get batch-specific data
            get_batch_data(frm, cdt, cdn, row.item_code, row.warehouse, row.batch_no);
        }
    },

    // Recalculate outgoing total when valuation_rate changes
    valuation_rate: function(frm, cdt, cdn) {
        frm.events.calculate_outgoing_total(frm);
    },

    // Recalculate outgoing total when quantity changes (if qty field exists)
    qty: function(frm, cdt, cdn) {
        frm.events.calculate_outgoing_total(frm);
    },

    repack_item_remove: function(frm, cdt, cdn) {
        frm.refresh_field('repack_item');
        // Recalculate total after removing row
        setTimeout(() => {
            frm.events.calculate_outgoing_total(frm);
        }, 100);
    }
});

// Function to calculate amount (qty * valuation_rate) for Target Item table
function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let qty = flt(row.qty) || 0;
    let valuation_rate = flt(row.valuation_rate) || 0;
    let amount = qty * valuation_rate;
    
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}

// Enhanced Bin data fetching function
function get_bin_data(frm, cdt, cdn, item_code, warehouse) {
    if (!item_code || !warehouse) {
        return;
    }

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bin',
            filters: {
                'item_code': item_code,
                'warehouse': warehouse
            },
            fields: ['valuation_rate', 'actual_qty', 'reserved_qty', 'projected_qty']
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let bin_data = r.message[0];
                frappe.model.set_value(cdt, cdn, 'valuation_rate', bin_data.valuation_rate || 0);
                frappe.model.set_value(cdt, cdn, 'avail_qty', bin_data.actual_qty || 0);
                
                // Set additional fields if they exist
                if (frappe.meta.has_field(cdt, 'reserved_qty')) {
                    frappe.model.set_value(cdt, cdn, 'reserved_qty', bin_data.reserved_qty || 0);
                }
                if (frappe.meta.has_field(cdt, 'projected_qty')) {
                    frappe.model.set_value(cdt, cdn, 'projected_qty', bin_data.projected_qty || 0);
                }
                
                // Calculate amount if this is Target Item table
                if (cdt === 'Target Item') {
                    calculate_amount(frm, cdt, cdn);
                }
                
                // Recalculate totals after updating valuation rate
                if (cdt === 'Repack Item') {
                    frm.events.calculate_outgoing_total(frm);
                } else if (cdt === 'Target Item') {
                    frm.events.calculate_incoming_total(frm);
                }
            } else {
                frappe.model.set_value(cdt, cdn, 'valuation_rate', 0);
                frappe.model.set_value(cdt, cdn, 'avail_qty', 0);
                
                // Calculate amount if this is Target Item table (will be 0)
                if (cdt === 'Target Item') {
                    calculate_amount(frm, cdt, cdn);
                }
                
                // Recalculate totals after clearing valuation rate
                if (cdt === 'Repack Item') {
                    frm.events.calculate_outgoing_total(frm);
                } else if (cdt === 'Target Item') {
                    frm.events.calculate_incoming_total(frm);
                }
                
               
            }
        },
        error: function(r) {
            console.error('Error fetching Bin data:', r);
            frappe.show_alert({
                message: __('Error fetching stock information'),
                indicator: 'red'
            });
        }
    });
}

// New function to get batch-specific data
function get_batch_data(frm, cdt, cdn, item_code, warehouse, batch_no) {
    if (!item_code || !warehouse || !batch_no) {
        return;
    }

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Stock Ledger Entry',
            filters: {
                'item_code': item_code,
                'warehouse': warehouse,
                'batch_no': batch_no,
                'is_cancelled': 0
            },
            fields: ['valuation_rate', 'qty_after_transaction'],
            order_by: 'posting_date desc, posting_time desc',
            limit: 1
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let latest_entry = r.message[0];
                
                // Update valuation rate from the latest stock ledger entry
                if (latest_entry.valuation_rate) {
                    frappe.model.set_value(cdt, cdn, 'valuation_rate', latest_entry.valuation_rate);
                }
                
                // Get batch quantity
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Batch',
                        filters: {
                            'name': batch_no
                        },
                        fields: ['*']
                    },
                    callback: function(batch_r) {
                        if (batch_r.message && batch_r.message.length > 0) {
                            let batch_data = batch_r.message[0];
                            
                            // Get actual qty for this batch in this warehouse
                            frappe.call({
                                method: 'erpnext.stock.utils.get_stock_balance',
                                args: {
                                    'item_code': item_code,
                                    'warehouse': warehouse,
                                    'batch_no': batch_no
                                },
                                callback: function(qty_r) {
                                    if (qty_r.message !== undefined) {
                                        frappe.model.set_value(cdt, cdn, 'avail_qty', qty_r.message);
                                    }
                                    
                                    // Recalculate totals
                                    if (cdt === 'Repack Item') {
                                        frm.events.calculate_outgoing_total(frm);
                                    }
                                }
                            });
                        }
                    }
                });
                
            } else {
            }
        },
        error: function(r) {
            console.error('Error fetching Batch data:', r);
            frappe.show_alert({
                message: __('Error fetching batch information'),
                indicator: 'red'
            });
        }
    });
}