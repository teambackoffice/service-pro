import frappe
import json

@frappe.whitelist()
def get_item_avail_qty(items):
    avail_qty = []
    items = json.loads(items)
    
    for item in items:
        receipt_doc = frappe.get_doc(item.get("receipt_document_type"), item.get("receipt_document"))
        
        if item.get("item_code"):
            item_warehouse = None
            for doc_item in receipt_doc.items: 
                if doc_item.item_code == item.get("item_code"):
                    item_warehouse = doc_item.warehouse
                    break
            
            if item_warehouse and frappe.db.exists("Bin", {"item_code": item.get("item_code"), "warehouse": item_warehouse}):
                bin_doc = frappe.get_doc("Bin", {"item_code": item.get("item_code"), "warehouse": item_warehouse})
                avail_qty.append({
                    "item_code": item.get("item_code"), 
                    "warehouse": item_warehouse,
                    "avail_qty": bin_doc.actual_qty
                })
            else:
                avail_qty.append({
                    "item_code": item.get("item_code"), 
                    "warehouse": item_warehouse,
                    "avail_qty": 0
                })
    
    return avail_qty

