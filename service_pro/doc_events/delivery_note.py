import frappe

def change_status(doc, method):
    for prod in doc.production:
        production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
        if len(production) > 0:
            frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
                          ("To Bill", prod.reference))
            frappe.db.commit()
