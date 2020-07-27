import frappe

@frappe.whitelist()
def on_submit_si(doc, method):
    for prod in doc.production:
        frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",("Completed", prod.reference))
        frappe.db.commit()

@frappe.whitelist()
def on_cancel_si(doc, method):
    for prod in doc.production:
        frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",("In Progress", prod.reference))
        frappe.db.commit()