# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import cint, flt
from datetime import datetime
class Production(Document):
	def on_update_after_submit(self):
		for i in self.raw_material:
			if i.production:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Completed",i.production))
				frappe.db.commit()
	def on_cancel(self):
		for i in self.raw_material:
			if i.production:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("In Progress", i.production))
				frappe.db.commit()

		se = frappe.db.sql(""" SELECT * FROM `tabStock Entry` WHERE production=%s """, self.name, as_dict=1)
		if len(se) > 0:
			for i in se:
				se_record = frappe.get_doc("Stock Entry", i.name)
				se_record.cancel()
	def on_submit(self):
		for i in self.raw_material:
			if i.production:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Completed",i.production))
				frappe.db.commit()
	def set_available_qty(self):
		time = datetime.now().time()
		date = datetime.now().date()
		for d in self.get('raw_material'):
			previous_sle = get_previous_sle({
				"item_code": d.item_code,
				"warehouse": d.warehouse,
				"posting_date": date,
				"posting_time": time
			})
			# get actual stock at source warehouse
			d.available_qty = previous_sle.get("qty_after_transaction") or 0

	def validate(self):
		if self.type == "Assemble":
			self.series = "SK-"
		elif self.type == "Disassemble":
			self.series = "SK-D-"
		elif self.type == "Service":
			self.series = "HA-"

	def check_raw_materials(self):
		for i in self.raw_material:
			if i.available_qty == 0:
				return False, i.item_code
		return True, ""
	def generate_se(self):
		check,item_code = self.check_raw_materials()
		allow_negative_stock = cint(frappe.db.get_value("Stock Settings", None, "allow_negative_stock"))
		if check or (not check and allow_negative_stock):
			doc_se = {
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture" if self.type == "Assemble" or self.type == "Service"  else "Repack",
				"items": self.get_se_items(),
				"production": self.name,
				"additional_costs": self.get_additional_costs()
			}

			frappe.get_doc(doc_se).insert(ignore_permissions=1).submit()
			if self.type == "Disassemble":
				self.generate_finish_good_se()
			return ""

		else:
			frappe.throw("Item " + item_code + " Has no available stock")
	def generate_finish_good_se(self):
		doc_se1 = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Manufacture",
			"production": self.name,
			"additional_costs": self.get_additional_costs(),
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

	def get_additional_costs(self):
		costs = []
		for i in self.additional_cost:
			costs.append({
				"expense_account": i.expense_ledger,
				"description": i.description,
				"amount": i.additional_cost_amount
			})
		return costs
	def generate_dn(self):
		if self.input_qty > self.qty_for_sidn:
			frappe.throw("Maximum qty that can be generated is " + str(self.qty))

		doc_dn = {
			"doctype": "Delivery Note",
			"customer": self.customer,
			"items": self.get_si_items("DN", self.input_qty),
			"production": self.get_production_items(self.input_qty),
		}
		dn = frappe.get_doc(doc_dn)
		dn.insert(ignore_permissions=1)
		return dn.name

	def generate_si(self):
		if self.input_qty > self.qty_for_sidn:
			frappe.throw("Maximum qty that can be generated is " + str(self.qty))

		doc_si = {
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"items": self.get_si_items("SI", self.input_qty),
			"production": self.get_production_items(self.input_qty),
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
			if item.available_qty > 0:
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
	def get_si_items(self, type, qty):


		obj = {
			'item_code': self.item_code_prod,
			'item_name': self.get_item_value("item_name"),
			'description': self.get_item_value("description"),
			'qty': qty,
			'uom': "Nos",
			'rate': self.rate,
			'cost_center': self.cost_center,
			'income_account': self.income_account
		}
		if type == "DN":
			obj["warehouse"] = self.warehouse
		return [obj]

	def get_production_items(self, qty):
		return [{
			'reference': self.name,
			'qty': qty,
			'rate': self.rate,
			'amount': self.amount,

		}]

	def get_item_value(self, field):
		items = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, self.item_code_prod, as_dict=1)
		return items[0][field]

@frappe.whitelist()
def get_rate(item_code, warehouse, based_on,price_list):
	time = datetime.now().time()
	date = datetime.now().date()
	balance = 0
	if warehouse:
		previous_sle = get_previous_sle({
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": date,
			"posting_time": time
		})
		# get actual stock at source warehouse
		balance = previous_sle.get("qty_after_transaction") or 0

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
def get_dn_or_si(name):
	si = frappe.db.sql(""" 
 			SELECT * FROM `tabSales Invoice Production` WHERE reference=%s and parenttype=%s """,
							 (name,"Sales Invoice"), as_dict=1)
	dn = frappe.db.sql(""" 
	 			SELECT * FROM `tabSales Invoice Production` WHERE reference=%s and parenttype=%s """,
					   (name, "Delivery Note"), as_dict=1)
	return len(si) > 0,len(dn) > 0

@frappe.whitelist()
def get_dn_si_qty(item_code, qty, name):
	si_query = """ 
 			SELECT SII.qty as qty FROM `tabSales Invoice` AS SI 
 			INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name
 			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
 			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1
 			"""
	si = frappe.db.sql(si_query,(name,"Sales Invoice"), as_dict=1)
	dn_query = """ 
	 			SELECT DNI.qty as qty FROM `tabDelivery Note` AS DN 
	 			INNER JOIN `tabDelivery Note Item` AS DNI ON DNI.parent = DN.name
	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1
	 			"""
	dn = frappe.db.sql(dn_query,(name, "Delivery Note"), as_dict=1)

	total_qty = 0

	if len(si) > 0:
		total_qty += si[0].qty

	if len(dn) > 0:
		total_qty += dn[0].qty
	print(si)
	print(dn)
	print(float(qty) - float(total_qty))
	return float(qty) - float(total_qty)


@frappe.whitelist()
def change_status(name):
	frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Partially Delivered", name))
	frappe.db.commit()
	return 1