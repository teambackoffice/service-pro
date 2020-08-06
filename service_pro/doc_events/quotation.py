import frappe

def on_cancel_quotation(doc, method):
    print("QUOTATION!!!!")
    frappe.db.sql(""" UPDATE `tabService Receipt Note` SET quotation="" WHERE name=%s  """, doc.service_receipt_note)
    frappe.db.commit()