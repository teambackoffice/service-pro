import frappe
import json

@frappe.whitelist()
def get_item_avail_qty(items):
    avail_qty = []
    items = json.loads(items)
    for item in items:
        warehouse = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE name=%s""".format(item.get("receipt_document_type")),item.get("receipt_document"),as_dict=1)

        if item.get("item_code"):
            if frappe.db.exists("Bin", {"item_code":item.get("item_code")}):
                bin = frappe.get_last_doc("Bin", {"item_code":item.get("item_code"),"warehouse":warehouse[0].set_warehouse})
                avail_qty.append({"item_code": item.get("item_code"), "avail_qty":bin.actual_qty})
    return avail_qty

