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
                        // Display the available stock details if data exists
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

                        // Set the HTML content to show stock details
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
        } else {
            // Clear the field if no item_code is selected
            frm.fields_dict.stock_details.$wrapper.empty();
        }
    }
});
