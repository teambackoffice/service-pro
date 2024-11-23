frappe.ui.form.on("Inter Company Material Request", {
    schedule_date: function(frm) {
        if (frm.doc.schedule_date) {
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "schedule_date", frm.doc.schedule_date);
            });
        }
    },
    refresh: function(frm) {
        frm.fields_dict.stock_details.$wrapper.empty();
        frm.fields_dict["items"].grid.get_field("supplier").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    is_internal_supplier: 1
                }
            };
        };

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
            // Fetch stock details
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
                        frm.fields_dict.stock_details.$wrapper.empty();
                        frappe.msgprint({
                            title: __('No Stock Data'),
                            message: __("insufficient Stock: {0}", [item.item_code]),
                            indicator: 'red'
                        });

                        // Automatically remove the row if no stock is available
                        frappe.model.clear_doc(cdt, cdn);
                        frm.refresh_field("items");
                    }
                }
            });

            // Fetch UOM and Item Name
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
    }
});
