import frappe

def update_item_valuation_rate(doc, method=None):
    print(doc.incoming_rate)
    if doc.item_code:
        item_doc = frappe.get_doc("Item", {"item_code":doc.item_code})
        item_doc.valuation_rate = doc.incoming_rate
        item_doc.save(ignore_permissions=True)
