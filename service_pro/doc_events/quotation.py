import frappe

@frappe.whitelist()
def get_rate(item_code):
    item = frappe.get_doc("Item", item_code)
    return item.standard_rate


def on_cancel_quotation(doc, method):
    print("QUOTATION!!!!")
    frappe.db.sql(""" UPDATE `tabService Receipt Note` SET quotation="" WHERE name=%s  """, doc.service_receipt_note)
    frappe.db.commit()