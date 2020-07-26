import frappe

@frappe.whitelist()
def get_rate(item_code):
    item = frappe.get_doc("Item", item_code)
    return item.standard_rate