frappe.ui.form.on("Inter Company Material Request", {
    schedule_date: function(frm) {
        if (frm.doc.schedule_date) {
            // Loop through each row in the child table
            frm.doc.items.forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "schedule_date", frm.doc.schedule_date);
            });
        }
    },
    refresh: function(frm) {
        // Set query for supplier field in child table
        frm.fields_dict["items"].grid.get_field("supplier").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    is_internal_supplier: 1
                }
            };
        };

        // Set query for set_warehouse field in the parent Doctype
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
                        frappe.throw({
                            title: __('Message'),
                            message: __('No available stock data found for this item.'),
                            indicator: 'blue'
                        });
                    }
                }
            });

            // Fetch UOM
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Item",
                    fieldname: "stock_uom",
                    filters: { name: item.item_code }
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
                    }
                }
            });
        } else {
            frm.fields_dict.stock_details.$wrapper.empty();
        }
    },
});
