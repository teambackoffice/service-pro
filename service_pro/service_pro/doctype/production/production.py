# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from erpnext.stock.utils import get_stock_balance
from frappe.model.document import Document
import ast
class Production(Document):
	def validate(self):
		if self.type == "Assemble":
			self.series = "SK-"
		elif self.type == "Disassemble":
			self.series = "SK-D-"
		elif self.type == "Service":
			self.series = "HA-"

	def generate_se(self):
		if self.type != "Service":
			doc_se = {
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture" if self.type == "Assemble" else "Repack",
				"items": self.get_se_items(),
				"production": self.name,
				"total_additional_costs": self.additional_cost_total
			}

			frappe.get_doc(doc_se).insert(ignore_permissions=1).submit()
			if self.type == "Disassemble":
				self.generate_finish_good_se()

		return ""
	def generate_finish_good_se(self):
		doc_se1 = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Manufacture",
			"production": self.name,
			"total_additional_costs": self.additional_cost_total,
			"items": [{
				'item_code': self.item_code_prod,
				't_warehouse': self.warehouse,
				'qty': self.qty,
				'uom': self.umo,
				'basic_rate': self.rate,
				'cost_center': self.cost_center
			}],
		}
		frappe.get_doc(doc_se1).insert(ignore_permissions=1).submit()

	def generate_dn(self):
		doc_dn = {
			"doctype": "Delivery Note",
			"customer": self.customer,
			"items": self.get_si_items(),
			"production": self.get_production_items(),
		}
		dn = frappe.get_doc(doc_dn)
		dn.insert(ignore_permissions=1)
		return dn.name

	def generate_si(self):
		doc_si = {
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"update_stock": 1,
			"items": self.get_si_items(),
			"production": self.get_production_items(),
		}
		si = frappe.get_doc(doc_si)
		si.insert(ignore_permissions=1)
		return si.name
	def generate_jv(self):
		doc_jv = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.posting_date,
			"accounts": self.jv_accounts(),
			"production": self.name
		}

		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()
	def jv_accounts(self):
		accounts = []
		amount = 0
		for item in self.advance_payment:
			amount += item.amount
			accounts.append({
				'account': item.expense_account,
				'debit_in_account_currency': item.amount,
				'credit_in_account_currency': 0,
			})
		debit_account = frappe.db.sql(""" SELECT * FROM `tabAccount` WHERE name like %s """, "%Debtors%",as_dict=1  )
		if len(debit_account) > 0:
			accounts.append({
				'account': debit_account[0].name,
				'debit_in_account_currency': 0,
				'credit_in_account_currency': amount,
				'party_type': "Customer",
				'party': self.customer,
				'is_advance': "Yes",
			})
		print(accounts)
		return accounts
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
		items.append({
			'item_code': self.item_code_prod,
			't_warehouse': self.warehouse,
			'qty': self.qty,
			'uom': self.umo,
			'basic_rate': self.rate,
			'cost_center': self.cost_center
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

	def get_item_value(self, field):
		items = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, self.item_code_prod, as_dict=1)
		return items[0][field]

@frappe.whitelist()
def get_rate(item_code, warehouse, based_on,price_list):
	print("diri baaa")
	balance = get_stock_balance(item_code,warehouse) if warehouse else 0

	condition = ""
	if price_list == "Standard Buying":
		condition += " and buying = 1 "
	elif price_list == "Standard Selling":
		condition += " and selling = 1 "
	query = """ SELECT * FROM `tabItem Price` WHERE item_code=%s {0} ORDER BY valid_from DESC LIMIT 1""".format(condition)

	item_price = frappe.db.sql(query,item_code, as_dict=1)
	rate = item_price[0].price_list_rate if len(item_price) > 0 else 0
	print(based_on)
	if based_on == "Valuation Rate":
		print("WALA DIR")
		item_price = frappe.db.sql(
			""" SELECT * FROM `tabItem` WHERE item_code=%s""",
			item_code, as_dict=1)
		rate = item_price[0].valuation_rate if len(item_price) > 0 else 0

	return rate, balance

@frappe.whitelist()
def get_uom(item_code):
	item = frappe.db.sql(
		""" SELECT * FROM `tabItem` WHERE name=%s""",
		item_code, as_dict=1)

	return item[0].stock_uom

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

@frappe.whitelist()
def get_jv(production):
	jv = frappe.db.sql(""" SELECT * FROM `tabJournal Entry` WHERE production=%s """, production, as_dict=1)
	return jv[0].name if len(jv) > 0 else ""

@frappe.whitelist()
def get_se(name):
	se = frappe.db.sql(""" SELECT * FROM `tabStock Entry` WHERE production=%s """, name, as_dict=1)
	return len(se) > 0

@frappe.whitelist()
def get_dn_or_si(name,doctype):
	dn_or_si = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Production` WHERE reference=%s and parenttype=%s """, (name,doctype), as_dict=1)
	return len(dn_or_si) > 0
