import frappe
import json

@frappe.whitelist()
def get_item_avail_qty(items):
    avail_qty = []
    items = json.loads(items)
    for item in items:
        if item.get("item_code"):
            if frappe.db.exists("Bin", {"item_code":item.get("item_code")}):
                bin = frappe.get_last_doc("Bin", {"item_code":item.get("item_code")})
                avail_qty.append({"item_code": item.get("item_code"), "avail_qty":bin.actual_qty})
    return avail_qty

