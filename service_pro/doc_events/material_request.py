import frappe
import json
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.get_item_details import get_item_defaults
from erpnext.buying.doctype.purchase_order.purchase_order import set_missing_values


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        if source.internal_supplier:
            target.supplier = source.internal_supplier
        elif args and args.get("supplier"):
            target.supplier = args.get("supplier")
            
            
            if source.custom_internal_supplier_name:
                target.custom_internal_supplier_name = source.custom_internal_supplier_name
       

    doc = get_mapped_doc(
        "Material Request",
        source_name,
        {
            "Material Request": {
                "doctype": "Purchase Order",
                "field_map": {
                    "custom_internal_supplier_name": "custom_internal_supplier_name",
                 
                },
            },
            
            "Material Request Item": {
                "doctype": "Purchase Order Item",
                "field_map": {
                    "stock_uom": "uom",
                },
            },
        },
        target_doc,
        set_missing_values
    )
    return doc

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
    if args is None:
        args = {}
    if isinstance(args, str):
        args = json.loads(args)

    def postprocess(source, target_doc):
        if frappe.flags.args and frappe.flags.args.default_supplier:
            supplier_items = []
            for d in target_doc.items:
                default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
                if frappe.flags.args.default_supplier == default_supplier:
                    supplier_items.append(d)
            target_doc.items = supplier_items

        set_missing_values(source, target_doc)

    def update_item(source_doc, target_doc, source_parent=None):
        """
        Customize this function to process individual items.
        Handles three arguments: source_doc, target_doc, and source_parent.
        """
        target_doc.schedule_date = source_doc.schedule_date
        target_doc.project = source_doc.project

    def select_item(d):
        filtered_items = args.get("filtered_children", [])
        child_filter = d.name in filtered_items if filtered_items else True
        return d.ordered_qty < d.stock_qty and child_filter

    doclist = get_mapped_doc(
        "Material Request",
        source_name,
        {
            "Material Request": {
                "doctype": "Purchase Order",
                "validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
            },
            "Material Request Item": {
                "doctype": "Purchase Order Item",
                "field_map": [
                    ["name", "material_request_item"],
                    ["parent", "material_request"],
                    ["uom", "stock_uom"],
                    ["uom", "uom"],
                    ["sales_order", "sales_order"],
                    ["sales_order_item", "sales_order_item"],
                    ["wip_composite_asset", "wip_composite_asset"],
                ],
                "postprocess": update_item,
                "condition": select_item,
            },
        },
        target_doc,
        postprocess,
    )

    doclist.set_onload("load_after_mapping", False)
    return doclist