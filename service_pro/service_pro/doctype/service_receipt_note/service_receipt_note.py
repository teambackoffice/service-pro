# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance

class ServiceReceiptNote(Document):
	def on_submit(self):

		for i in self.materials:
			item = frappe.get_doc("Item", i.materials)
			doc = {
				"doctype": "Inspection",
				"customer": self.customer,
				"customer_reference": self.customer_ref,
				"item_code": i.materials,
				"qty": i.qty,
				"rate": item.standard_rate,
				"amount": item.standard_rate * i.qty,
				"service_receipt_note": self.name
			}

			frappe.get_doc(doc).insert()
	def submit_inspections(self):
		inspections = frappe.db.sql(""" SELECT * FROM `tabInspection` WHERE service_receipt_note=%s""",self.name, as_dict=1)
		for inspection in inspections:
			record = frappe.get_doc("Inspection", inspection.name)
			record.submit()
		frappe.msgprint("Done Submitting Inspections")
