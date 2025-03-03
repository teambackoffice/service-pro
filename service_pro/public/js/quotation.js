frappe.ui.form.on("Quotation", {
    onload: function(frm) {
        // Warehouse filtering based on company
        frm.set_query("warehouse", "items", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            let query = {
                filters: [["Warehouse", "company", "in", ["", cstr(frm.doc.company)]]],
            };
            if (row.item_code) {
                query.query = "erpnext.controllers.queries.warehouse_query";
                query.filters.push(["Bin", "item_code", "=", row.item_code]);
            }
            return query;
        });

        // Role-based permission control
        frappe.call({
            method: "service_pro.doc_events.quotation.get_role",
            callback: function(r) {
                if (r.message) {
                    const authorized_role = r.message; 
                    console.log("Authorized Role:", authorized_role);
        
                    frappe.user_roles.includes(authorized_role)
                        ? frm.set_df_property('custom_ignore_permission_', 'read_only', 0) // Enable field
                        : frm.set_df_property('custom_ignore_permission_', 'read_only', 1); // Disable field
                } else {
                    console.error("No authorized role found.");
                }
            }
        });
    },

    party_name: function(frm) {
      
        console.log("party_name field changed:", frm.doc.party_name);
        
        if (frm.doc.party_name) {
            console.log("Fetching Sales Person for:", frm.doc.party_name);
            fetch_sales_person(frm, frm.doc.party_name);
        } else {
            console.log("No Customer selected, clearing Sales Person field.");
            frm.set_value('custom_sales_person', null);
        }
    }
    ,

    refresh: function(frm) {
        // Remove default Sales Order button
        setTimeout(() => {
            frm.remove_custom_button('Sales Order', "Create");
        }, 100);

        // Add Custom Sales Order Button
        if (frm.doc.docstatus == 1 && !["Lost", "Ordered"].includes(frm.doc.status)) {
            if (
                frappe.boot.sysdefaults.allow_sales_order_creation_for_expired_quotation ||
                !frm.doc.valid_till ||
                frappe.datetime.get_diff(frm.doc.valid_till, frappe.datetime.get_today()) >= 0
            ) {
                frm.add_custom_button(__("Sales order"), () => make_sales_order(frm), __("Create"));
            }

            if (frm.doc.status !== "Ordered") {
                frm.add_custom_button(__("Set as Lost"), () => {
                    frm.trigger("set_as_lost_dialog");
                });
            }

            cur_frm.page.set_inner_btn_group_as_primary(__("Create"));
        }
    }
});

// Fetch Sales Person for selected Customer
function fetch_sales_person(frm, customer) {
    console.log("fetch_sales_person() called for Customer:", customer);

    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Customer',
            name: customer,
        },
        callback: function(r) {
            console.log("Response received from Frappe:", r);

            if (r.message) {
                let sales_team = r.message.sales_team || [];
                console.log("Sales Team Data:", sales_team);

                if (Array.isArray(sales_team) && sales_team.length > 0 && sales_team[0].sales_person) {
                    let sales_person = sales_team[0].sales_person;
                    console.log("✅ Sales Person found:", sales_person);
                    frm.set_value('custom_sales_person', sales_person);
                } else {
                    console.log("❌ No Sales Person found for this Customer.");
                    frm.set_value('custom_sales_person', null);
                    frappe.msgprint(__('No Sales Person found for the selected Customer'));
                }
            } else {
                console.log("❌ No response data for the given Customer.");
            }
        }
    });
}
// Custom Sales Order Creation
function make_sales_order(frm) {
    let has_alternative_item = frm.doc.items.some((item) => item.is_alternative);
    if (has_alternative_item) {
        show_alternative_items_dialog(frm);
    } else {
        frappe.model.open_mapped_doc({
            method: "service_pro.doc_events.quotation.make_sales_order_so",
            frm: frm,
        });
    }
}

// Alternative Items Selection Dialog
function show_alternative_items_dialog(frm) {
    const table_fields = [
        {
            fieldtype: "Data",
            fieldname: "name",
            label: __("Name"),
            read_only: 1,
        },
        {
            fieldtype: "Link",
            fieldname: "item_code",
            options: "Item",
            label: __("Item Code"),
            read_only: 1,
            in_list_view: 1,
            columns: 2,
            formatter: (value, df, options, doc) => {
                return doc.is_alternative ? `<span class="indicator yellow">${value}</span>` : value;
            },
        },
        {
            fieldtype: "Data",
            fieldname: "description",
            label: __("Description"),
            in_list_view: 1,
            read_only: 1,
        },
        {
            fieldtype: "Currency",
            fieldname: "amount",
            label: __("Amount"),
            options: "currency",
            in_list_view: 1,
            read_only: 1,
        },
        {
            fieldtype: "Check",
            fieldname: "is_alternative",
            label: __("Is Alternative"),
            read_only: 1,
        },
    ];

    let data = frm.doc.items
        .filter((item) => item.is_alternative || item.has_alternative_item)
        .map((item) => {
            return {
                name: item.name,
                item_code: item.item_code,
                description: item.description,
                amount: item.amount,
                is_alternative: item.is_alternative,
            };
        });

    const dialog = new frappe.ui.Dialog({
        title: __("Select Alternative Items for Sales Order"),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                read_only: 1,
            },
            {
                fieldname: "alternative_items",
                fieldtype: "Table",
                cannot_add_rows: true,
                cannot_delete_rows: true,
                in_place_edit: true,
                reqd: 1,
                data: data,
                description: __("Select an item from each set to be used in the Sales Order."),
                get_data: () => {
                    return data;
                },
                fields: table_fields,
            },
        ],
        primary_action: function() {
            frappe.model.open_mapped_doc({
                method: "service_pro.doc_events.quotation.make_sales_order_so",
                frm: frm,
                args: {
                    selected_items: dialog.fields_dict.alternative_items.grid.get_selected_children(),
                },
            });
            dialog.hide();
        },
        primary_action_label: __("Continue"),
    });

    dialog.fields_dict.info.$wrapper.html(
        `<p class="small text-muted">
            <span class="indicator yellow"></span>
            ${__("Alternative Items")}
        </p>`
    );
    dialog.show();
}
