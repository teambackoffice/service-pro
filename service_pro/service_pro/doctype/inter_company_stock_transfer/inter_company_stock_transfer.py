# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InterCompanyStockTransfer(Document):
	def on_submit(self):
		self.first_se()
		self.second_se()
	def first_se(self):
		obj = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Issue",
			"posting_date":self.posting_date,
			"posting_time":self.time,
			"from_warehouse": self.from_warehouse,
			"company": self.from_company,
			"custom_inter_company_stock_transfer": self.name

		}
		items= []
		for x in self.item_details:
			items.append({
				"item_code": x.item_code,
				"qty": x.qty,
				"s_warehouse": self.from_warehouse,
				"basic_rate": x.value,
				"expense_account": self.from_company_debit_account,
				"cost_center": self.from_cost_center,
			})
		obj['items'] = items
		se = frappe.get_doc(obj).insert(ignore_permissions=1)
		se.submit()
	def second_se(self):
		obj = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"posting_date":self.posting_date,
			"posting_time":self.time,
			"to_warehouse": self.from_warehouse,
			"company": self.to_company,
			"custom_inter_company_stock_transfer": self.name
		}
		items = []
		for x in self.item_details:
			items.append({
				"item_code": x.item_code,
				"qty": x.qty,
				"s_warehouse": self.from_warehouse,
				"basic_rate": x.credit_value,
				"expense_account": self.to_company_credit_account,
				"cost_center": self.to_cost_center,
			})
		obj['items'] = items
		se = frappe.get_doc(obj).insert(ignore_permissions=1)
		se.submit()
	@frappe.whitelist()
	def get_avail_qty(self,item):
		bin = frappe.db.sql(""" SELECT * FROM `tabBin` WHERE item_code=%s and warehouse=%s """,(item['item_code'],self.from_warehouse),as_dict=1)

		return bin[0] if len(bin) > 0 else 0

	@frappe.whitelist()
	def get_defaults(self):
		print("--------------------------------------------------------------------------")
		defaults = {}

		if self.from_company:
			tables = [
				"Inter Company Stock Transfer From",
			]
			for table in tables:
				data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.from_company,
									 as_dict=1)
				if len(data) > 0:
					defaults[data[0].parentfield] = data[0]

			self.from_warehouse = defaults['from_companies'].warehouse if 'from_companies' in defaults else ""
			self.from_company_debit_account = defaults['from_companies'].account if 'from_companies' in defaults else ""
			self.from_cost_center = defaults['from_companies'].cost_center if 'from_companies' in defaults else ""

		if self.to_company:
			tables = [
				"Inter Company Stock Transfer To",
			]
			for table in tables:
				data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.to_company,
									 as_dict=1)
				if len(data) > 0:
					defaults[data[0].parentfield] = data[0]

			self.to_warehouse = defaults['to_companies'].warehouse if 'to_companies' in defaults else ""
			self.to_company_credit_account = defaults['to_companies'].account if 'to_companies' in defaults else ""
			self.to_cost_center = defaults['to_companies'].cost_center if 'from_companies' in defaults else ""

		return defaults