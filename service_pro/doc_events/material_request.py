import frappe
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
