import frappe


@frappe.whitelist()
def execute():
    fields = ["Customer-sales_man","Customer-sales_man_name"]

    for x in fields:
        frappe.db.sql(""" DELETE FROM `tabCustom Field` WHERE name=%s """,x)
        frappe.db.commit()