import frappe
from datetime import datetime
from frappe import _

def update_supplier_packing_slip(doc, method):
    pr = frappe.get_doc("Purchase Receipt", doc.name)
    for item in pr.items:
        supplier_packing_slip = item.custom_supplier_packing_slip
        
        if supplier_packing_slip:
            sp = frappe.get_doc("Supplier Packing Slip", supplier_packing_slip)
            sp.purchase_receipt = 1
            sp.save()