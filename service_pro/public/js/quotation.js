frappe.ui.form.on("Quotation", {
    onload : function(frm) {
        frm.set_query("warehouse", "items", function (doc, cdt, cdn) {
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
    },
    refresh: function (frm) {
        setTimeout(() => {
            frm.remove_custom_button('Sales Order', "Create");
    }, 100);
if (frm.doc.docstatus == 1 && !["Lost", "Ordered"].includes(frm.doc.status)) {
    if (
        frappe.boot.sysdefaults.allow_sales_order_creation_for_expired_quotation ||
        !frm.doc.valid_till ||
        frappe.datetime.get_diff(frm.doc.valid_till, frappe.datetime.get_today()) >= 0
    ) 

    {
        
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

    data = frm.doc.items
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
        primary_action: function () {
            frappe.model.open_mapped_doc({
                method: "service_pro.doc_events.quotation.make_sales_order_so",
                frm: me.frm,
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