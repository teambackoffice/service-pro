import frappe
@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        # Set the supplier field in Purchase Order from internal_supplier in Material Request
        if source.internal_supplier:
            target.supplier = source.internal_supplier
        elif args and args.get("supplier"):
            target.supplier = args.get("supplier")
       

    # Map fields from Material Request to Purchase Order
    doc = get_mapped_doc(
        "Material Request",
        source_name,
        {
            "Material Request": {
                "doctype": "Purchase Order",
                "field_map": {
                    # Add field mappings if required
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
