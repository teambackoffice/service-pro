# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Production(Document):
	def on_submit(self):
		if self.type != "Service":
			doc_se = {
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture" if self.type == "Assemble" else "Repack",
				"from_warehouse": self.raw_material_warehouse,
				"items": self.get_se_items(),
			}
			frappe.get_doc(doc_se).insert(ignore_permissions=1).submit()


		doc_si = {
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"update_stock": 1,
			"items": self.get_si_items(),
			"production": self.get_production_items(),
			"packed_items": self.get_si_packed_items()
		}
		frappe.get_doc(doc_si).insert(ignore_permissions=1)

	def get_se_items(self):
		items = []

		for item in self.raw_material:
			items.append({
				'item_code': item.item_code,
				's_warehouse': self.raw_material_warehouse,
				'qty': item.qty,
				'uom': "Nos",
				'basic_rate': item.rate,
				'cost_center': item.cost_center
			})
		return items
	def get_si_items(self):
		return [
					{
						'item_code': self.item_code,
						'item_name': self.get_item_value("item_name"),
						'description': self.get_item_value("description"),
						'qty': self.qty,
						'uom': "Nos",
						'rate': self.rate,
						'cost_center': self.cost_center,
						'income_account': self.income_account
					}
				]

	def get_production_items(self):
		return [
					{
						'reference': self.name,
						'qty': self.qty,
						'rate': self.rate,
						'amount': self.amount,

					}
				]

	def get_si_packed_items(self):
		items = []

		for item in self.raw_material:
			items.append({
				'parent_item': self.item_code,
				'item_code': item.item_code,
				'warehouse': self.raw_material_warehouse,
				'qty': item.qty,
			})

		return items


	def get_item_value(self, field):
		items = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, self.item_code, as_dict=1)
		return items[0][field]

