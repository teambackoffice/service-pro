import frappe

def on_trash_f(doc, method):
    print("GANAAAAAA")
    inspection = frappe.get_doc(doc.attached_to_doctype, doc.attached_to_name)
    if inspection.docstatus == 1:

        frappe.throw("You cannot remove attachment on submitted document")