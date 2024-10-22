import frappe

def validate(doc, method):
    for item in doc.items:
        if not item.purchase_order:
            frappe.throw(f"Purchase Order ID Missing {item.item_code} in the row {item.idx}")
