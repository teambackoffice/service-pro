import frappe

def update_item_valuation_rate(doc, method=None):
    if doc.item_code:
        item_doc = frappe.get_doc("Item", {"item_code": doc.item_code})
        
        if doc.company == "NOOR NAJI AL MASKEN CONTRACTING EST":
            item_doc.valuation_rate = doc.incoming_rate
            item_doc.save(ignore_permissions=True)
        else:
            frappe.log_error(f"Unhandled company: {doc.company}", "Valuation Rate Update Error")