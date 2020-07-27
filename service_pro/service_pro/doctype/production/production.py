# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.stock.utils import get_stock_balance
from frappe.model.document import Document

class Production(Document):
	def validate(self):
		if self.type == "Assemble":
			self.series = "SK-"
		elif self.type == "Disassemble":
			self.series = "SK-D-"
		elif self.type == "Service":
			self.series = "HA-"
	def on_submit(self):
		if self.type != "Service":
			doc_se = {
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture" if self.type == "Assemble" else "Repack",
				"from_warehouse": self.raw_material_warehouse,
				"items": self.get_se_items(),
			}
			frappe.get_doc(doc_se).insert(ignore_permissions=1).submit()

	def generate_si(self):
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
				's_warehouse': item.warehouse,
				'qty': item.qty_raw_material,
				'uom': "Nos",
				'basic_rate': item.rate_raw_material,
				'cost_center': item.cost_center
			})
		return items
	def get_si_items(self):
		return [
					{
						'item_code': self.item_code_prod,
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
				'parent_item': self.item_code_prod,
				'item_code': item.item_code,
				'warehouse': item.warehouse,
				'qty': item.qty_raw_material,
			})

		return items


	def get_item_value(self, field):
		items = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, self.item_code_prod, as_dict=1)
		return items[0][field]

@frappe.whitelist()
def get_rate(item_code, warehouse):
	item_price = frappe.db.sql(
		""" SELECT * FROM `tabItem Price` WHERE item_code=%s and selling=1 ORDER BY valid_from DESC LIMIT 1""",
		item_code, as_dict=1)
	if warehouse:
		print(get_stock_balance(item_code, warehouse))

	return item_price[0].price_list_rate if len(item_price) > 0 else 0, get_stock_balance(item_code,warehouse) if warehouse else 0

@frappe.whitelist()
def get_address(customer):
	address = frappe.db.sql(""" 
 						SELECT
 						 	A.name,
 							A.address_line1, 
							A.city, 
							A.county ,
							A.state,
							A.country,
							A.pincode
						FROM `tabAddress` AS A 
 						INNER JOIN `tabDynamic Link` AS DL 
 						ON DL.link_doctype=%s and DL.link_name=%s and DL.parent = A.name
 						WHERE A.is_primary_address=1  """,("Customer", customer), as_dict=1)
	return address[0] if len(address) > 0 else {}
# SELECT
#  		I.id,
#  		I.description,
#  		SUM(DD.quantity) as received_qty,
#  		SUM(IR.quantity) as released_qty,
# 	SUM(DD.quantity) - SUM(IR.quantity) as balance
#  FROM items AS I
#  INNER JOIN users AS U ON U.office =  'DDOPH-Montevista'
#  INNER JOIN delivery_details AS DD ON DD.user_id = U.id and DD.items_id = I.id
#  INNER JOIN item_release AS IR ON IR.delivery_id = DD.deliveries_id and IR.items_id = I.id
#  GROUP BY I.id LIMIT 0,25