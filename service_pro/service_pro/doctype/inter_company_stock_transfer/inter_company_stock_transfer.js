// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt
var defaults = {};

function compute_totals(cur_frm) {
    var total_qty = 0;
    var debit_value = 0;
    var credit_value = 0;

    for (var x = 0; x < cur_frm.doc.item_details.length; x += 1) {
        if (cur_frm.doc.item_details[x].qty > cur_frm.doc.item_details[x].available_qty) {
            cur_frm.doc.item_details[x].qty = 0;
            cur_frm.refresh_field("item_details");
            frappe.throw("Qty Cannot Be More Than Available Qty");
        }

        total_qty += cur_frm.doc.item_details[x].qty;
        debit_value += cur_frm.doc.item_details[x].value;
        credit_value += cur_frm.doc.item_details[x].credit_value;
    }

    cur_frm.doc.deference_value = debit_value - credit_value;
    cur_frm.doc.total_qty = total_qty;
    cur_frm.doc.debit_value = debit_value;
    cur_frm.doc.credit_value = credit_value;
    cur_frm.refresh_fields(["deference_value", "total_qty", "debit_value", "credit_value"]);
}

frappe.ui.form.on("Inter Company Stock Transfer Item", {
    item_code: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (d.item_code) {
            cur_frm.call({
                doc: cur_frm.doc,
                method: "get_avail_qty",
                args: {
                    item: d
                },
                freeze: true,
                freeze_message: "Getting Available Qty",
                callback: function (r) {
                    d.available_qty = r.message.actual_qty;
                    d.value = r.message.valuation_rate;
                    d.credit_value = r.message.valuation_rate;
                    cur_frm.refresh_field(d.parentfield);
                    compute_totals(cur_frm);
                }
            });
        }
    },
    qty: function (frm, cdt, cdn) {
        compute_totals(cur_frm);
    },
    credit_value: function (frm, cdt, cdn) {
        compute_totals(cur_frm);
    },
    item_details_remove: function () {
        compute_totals(cur_frm);
    },
});

frappe.ui.form.on("Inter Company Stock Transfer", {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.clear_custom_buttons();

            if (!frm.doc.is_received) {
                frm.add_custom_button(__("Update Qty"), () => {
                    erpnext.utils.update_child_items({
                        frm,
                        child_docname: "item_details",
                        cannot_add_row: false,
                        has_reserved_stock: frm.doc.__onload?.has_reserved_stock,
                    });
                });
            }

            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Production Settings",
                    fieldname: ["in_transit_user_role", "received_user_role"]
                },
                callback: function (res) {
                    if (res.message) {
                        const in_transit_role = res.message.in_transit_user_role;
                        const received_role = res.message.received_user_role;

                        // Ensure Administrator always sees the buttons
                        const is_admin = frappe.user_roles.includes("Administrator");

                        if ((frappe.user_roles.includes(in_transit_role) || is_admin) && frm.doc.in_transit != 1) {
                            frm.add_custom_button(__('In Transit'), function () {
                                frappe.confirm(
                                    __('Are you sure you want to mark this as In Transit?'),
                                    function () {
                                        frappe.call({
                                            method: "service_pro.service_pro.doctype.inter_company_stock_transfer.inter_company_stock_transfer.create_material_transfer",
                                            args: {
                                                name: frm.doc.name
                                            },
                                            callback: function (r) {
                                                if (r.message) {
                                                    frappe.msgprint(__('Material Transfer created successfully: {0}', [r.message]));
                                                    frm.reload_doc();
                                                }
                                            }
                                        });
                                    }
                                );
                            }, __("Create"));
                        }

                        if ((frappe.user_roles.includes(received_role) || is_admin) && !frm.doc.is_received) {
                            frm.add_custom_button(__('Received'), function () {
                                frappe.confirm(
                                    __('Are you sure you want to mark this as Received?'),
                                    function () {
                                        frappe.call({
                                            method: "service_pro.service_pro.doctype.inter_company_stock_transfer.inter_company_stock_transfer.reserve_material_transfer",
                                            args: {
                                                name: frm.doc.name
                                            },
                                            callback: function (r) {
                                                if (r.message) {
                                                    frappe.msgprint(__('Material Issue and Receipt created successfully.'));
                                                    frappe.db.set_value(
                                                        "Inter Company Stock Transfer",
                                                        frm.doc.name,
                                                        "is_received",
                                                        1
                                                    ).then(() => {
                                                        frm.reload_doc();
                                                    });
                                                }
                                            }
                                        });
                                    }
                                );
                            }, __("Create"));
                        }
                    }
                }
            });
        }
    },
    onload: function(frm) {
        // Setup batch_no filter for item_details child table
        frm.fields_dict["item_details"].grid.get_field("batch_no").get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row && row.item_code) {
                return {
                    query: "erpnext.controllers.queries.get_batch_no",
                    filters: {
                        "item_code": row.item_code
                    }
                };
            }
            return {};
        };
    },

    // Removed auto_fill_credit_value function as it's no longer needed
    
    before_submit: function(frm) {
        frm.doc.item_details.forEach(item => {
            if (!item.credit_value) {
                frappe.throw(__('Credit Value is required'));
            }
            if (!item.value) {
                frappe.throw(__('Debit Value is required'));
            }
        });
        
    },
});

erpnext.utils.update_child_items = function (opts) {
    const frm = opts.frm;
    const cannotAddRow = opts.cannot_add_row ?? true;
    const childDocname = opts.child_docname || "item_details";
    const hasReservedStock = opts.has_reserved_stock || false;
    const childMeta = frappe.get_meta(`${frm.doc.doctype} Item`);

    const getPrecision = (fieldname) => {
        const field = childMeta.fields.find((f) => f.fieldname === fieldname);
        return field?.precision || 2; 
    };

    const data = frm.doc[childDocname].map((item) => ({
        docname: item.name,
        item_code: item.item_code,
        item_name: item.item_name,
        qty: item.qty,
        received_qty: item.received_qty,
        rate: item.rate,
        uom: item.uom,
    }));

    const fields = [
        { fieldtype: "Data", fieldname: "docname", hidden: 1 },
        {
            fieldtype: "Link",
            fieldname: "item_code",
            options: "Item",
            in_list_view: 1,
            label: __("Item Code"),
            get_query: () => ({ query: "erpnext.controllers.queries.item_query", filters: { is_stock_item: 1 } }),
        },
        {
            fieldtype: "Data",
            fieldname: "item_name",
            label: __("Item Name"),
            in_list_view: 1, 
            read_only: 1, 
        },
        {
            fieldtype: "Float",
            fieldname: "qty",
            label: __("Issued Qty"),
            read_only: 1,
            precision: getPrecision("qty"),
            in_list_view: 1,
        },
        {
            fieldtype: "Float",
            fieldname: "received_qty",
            label: __("Received Qty"),
            precision: getPrecision("qty"),
            in_list_view: 1,
        },
    ];

    const dialog = new frappe.ui.Dialog({
        title: __("Update Items"),
        size: "extra-large",
        fields: [
            {
                fieldname: "trans_items",
                fieldtype: "Table",
                label: __("Items"),
                cannot_add_rows: cannotAddRow,
                in_place_edit: false,
                reqd: 1,
                data,
                fields,
            },
        ],
        primary_action_label: __("Update"),
        primary_action() {
            if (frm.doctype === "Inter Company Stock Transfer" && hasReservedStock) {
                frappe.confirm(
                    __("The reserved stock will be released when you update items. Are you sure you want to proceed?"),
                    () => this.updateItems()
                );
            } else {
                this.updateItems();
            }
        },
        updateItems() {
            const transItems = this.get_values().trans_items.filter((item) => item.item_code);
            console.log(transItems)
            frappe.call({
                method: "service_pro.service_pro.doctype.inter_company_stock_transfer.inter_company_stock_transfer.update_child_qty_rate",
                freeze: true,
                args: {
                    parent_doctype: frm.doc.doctype,
                    parent_doctype_name: frm.doc.name,
                    trans_items: transItems,
                    child_docname: childDocname,
                },
                callback: () => frm.reload_doc(),
            });
            this.hide();
            refresh_field(childDocname);
        },
    });

    dialog.show();
};


// 	from_company: function () {
//        if(cur_frm.doc.from_company){
//             cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }
//     },
//     to_company: function () {
//        if(cur_frm.doc.to_company){
//             cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }
//     },
//     onload: function (frm) {
// 	    if(cur_frm.is_new()){
// 	       cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "get_defaults",
//                 freeze: true,
//                 freeze_message: "Getting Company Defaults....",
//                 callback: function (r) {
//                     defaults = r.message

//                 }
//             })
//         }

//     }

