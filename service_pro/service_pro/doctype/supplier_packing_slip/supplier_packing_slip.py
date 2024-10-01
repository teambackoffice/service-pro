# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class SupplierPackingSlip(Document):
	def on_submit(self):
          for item in self.supplier_packing_slip_item:
               if item.qty ==0:
                    frappe.throw(_("Cannot submit Packing Slip with zero quantity item"))	


@frappe.whitelist()
def make_purchase_receipt(packing_slip):

    packing = frappe.get_doc("Supplier Packing Slip", packing_slip)
    order = frappe.get_doc("Purchase Order", packing.purchase_order)
  
    
    pr = frappe.get_doc({
        'doctype': 'Purchase Receipt',
        'posting_date': packing.posting_date,
        'company': packing.company,
        'supplier': packing.supplier
    })


    for item in packing.supplier_packing_slip_item:
        po_item = frappe.get_doc("Purchase Order Item", item.purchase_order_item)
        pr_item = pr.append("items", {})
        pr_item.item_code = item.item_code
        pr_item.item_name = po_item.item_name
        pr_item.uom = item.uom
        pr_item.qty = item.qty
        pr_item.item_group = po_item.item_group
        pr_item.rate = po_item.rate
        pr_item.purchase_order = item.po_ref
        pr_item.custom_supplier_packing_slip = item.parent
        pr_item.purchase_order_item = item.purchase_order_item
        
    pr.taxes = order.taxes
    pr.insert(ignore_permissions=True)

    return pr.name