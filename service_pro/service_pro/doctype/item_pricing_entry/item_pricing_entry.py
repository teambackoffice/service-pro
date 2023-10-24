# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ItemPricingEntry(Document):
	def on_submit(self):
		frappe.msgprint("Item Price creation started for {0} groups".format(len(self.item_groups)))
		frappe.enqueue(
			method=self.create_price_list,
			queue='short'
		)
	def create_price_list(self):
		for row in self.item_groups:
			filters = {
				"item_group": row.item_group,
				"custom_brand_name": row.brand,
				"custom_item_specification": row.item_specification
			}
			item_list = frappe.db.get_list("Item", filters, ['item_code', 'valuation_rate'], ignore_permissions=True)
			for item in item_list:
				price_doc = frappe.new_doc("Item Price")
				price_doc.item_code = item.item_code
				price_doc.price_list = row.price_list
				price_doc.valid_from = self.valid_from
				price_doc.price_list_rate = item.valuation_rate + (item.valuation_rate * (row.item_price_percentage/100))
				price_doc.save(ignore_permissions=True)


