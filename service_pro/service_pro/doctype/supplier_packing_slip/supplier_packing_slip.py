# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import _


class SupplierPackingSlip(Document):
	def on_submit(self):
          for item in self.supplier_packing_slip_item:
               if item.qty ==0:
                    frappe.throw(_("Cannot submit Packing Slip with zero quantity item"))	



@frappe.whitelist()
def make_purchase_receipt(packing_slip):
    def map_items(source_doc, target_doc, source_parent):
        target_doc.update({
            'item_code': source_doc.item_code,
            'qty': source_doc.qty,
            'uom': source_doc.uom,
            'purchase_order': source_doc.po_ref,
            'purchase_order_item': source_doc.purchase_order_item,
            'custom_supplier_packing_slip': source_doc.parent,
            'use_serial_batch_fields': 1
        })

    pr = get_mapped_doc(
        "Supplier Packing Slip",
        packing_slip,
        {
            "Supplier Packing Slip": {
                "doctype": "Purchase Receipt",
                "field_map": {
                    "posting_date": "posting_date",
                    "company": "company",
                    "supplier": "supplier",
                },
            },
            "Supplier Packing Slip Item": {
                "doctype": "Purchase Receipt Item",
                "postprocess": map_items,
            },
        },
        ignore_permissions=True
    )

    pr.insert(ignore_permissions=True)
    return pr.name
