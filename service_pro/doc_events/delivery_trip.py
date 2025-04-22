import frappe
from frappe.contacts.doctype.address.address import get_address_display

@frappe.whitelist()
def get_billing_address_by_title(company_name):
    address = frappe.get_all("Address", filters={
        "address_title": company_name,
        "address_type": "Billing",
        "disabled": 0
    }, fields=["name"], limit=1)

    if address:
        return get_address_display(address[0].name)
    
    return ""
