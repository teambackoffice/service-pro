# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import cint, flt
from erpnext.stock.utils import get_stock_balance
from datetime import datetime

class Production(Document):
	def before_submit(self):
		if not self.ignore_permission and not self.sales_order:
			frappe.throw("Sales Order is Required")

	@frappe.whitelist()
	def calculate_total_selling_rate(self):
		"""Calculate total selling rate from item_selling_price_list table"""
		total = 0
		for row in self.item_selling_price_list:
			if row.selling_rate:
				total += flt(row.selling_rate)
		
		self.total_selling_rate = total
		return total

	@frappe.whitelist()
	def get_defaults(self):
		if self.company:
			defaults = {
				"item_naming_series": frappe.db.get_value("Production Settings", None, "item_naming_series") or "",
				"item_group": frappe.db.get_value("Production Settings", None, "item_group") or "",
				# "finish_good_cost_center": frappe.db.get_value("Production Settings", None, "finish_good_cost_center") or "",
				"credit_note_user_role": frappe.db.get_value("Production Settings", None, "credit_note_user_role") or "",
				"debit_note_user_role": frappe.db.get_value("Production Settings", None, "debit_note_user_role") or "",
				# "income_account": frappe.db.get_value("Production Settings", None, "income_account") or "",
				# "finish_good_warehouse": frappe.db.get_value("Production Settings", None, "finish_good_warehouse") or "",
				"mandatory_additional_cost_in_production": frappe.db.get_value("Production Settings", None, "mandatory_additional_cost_in_production") or 0,
				"enable_sales_order_validation": frappe.db.get_value("Production Settings", None, "enable_sales_order_validation") or 0,
				"automatically_create_jv": frappe.db.get_value("Production Settings", None, "automatically_create_jv") or 0,
			}
			tables = [
				"Raw Material Defaults",
				"Site Job Report Settings",
				"Inspection Settings",
				"Incentive Journal",
				"Sales Partner Payments Details",
				"Inter Company Stock Transfer From",
				"Inter Company Stock Transfer To",
				"Finish Good Defaults"
			]
			for table in tables:
				data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table),self.company,as_dict=1)
				if len(data) > 0:
					defaults[data[0].parentfield] = data[0]

			self.warehouse = defaults.get('finish_good_defaults', {}).get('finish_good_warehouse', "")
			self.cost_center = defaults.get('finish_good_defaults', {}).get('finish_good_cost_center', self.cost_center)
			self.income_account = defaults.get('finish_good_defaults', {}).get('income_account', "")
			self.rate_of_materials_based_on = defaults.get('raw_material_defaults', {}).get('rate_of_materials_based_on', "")
			self.price_list = defaults.get('price_list', "")
			return defaults

	@frappe.whitelist()
	def generate_item(self):
		if not self.item_name:
			frappe.throw("Please add a valid item name")
		if not self.umo:
			frappe.throw("Please add a valid UOM")

		# Fetch values from Production Settings
		item_group = frappe.db.get_value("Production Settings", None, "item_group")
		tax_template = frappe.db.get_value("Production Settings", None, "default_item_tax_template")
		item_naming_series = frappe.db.get_value("Production Settings", None, "item_naming_series")

		if not item_group:
			frappe.throw("Please set the default item group in Production Settings")
		if not item_naming_series:
			frappe.throw("Please set the default Naming Series in Production Settings")
		doctype = {
			"doctype": "Item",
			"item_name": self.item_name,
			"stock_uom": self.umo,
			"item_group": self.item_group,
			"naming_series": item_naming_series,
			"custom_tax_template": tax_template,
		}

		item = frappe.get_doc(doctype)

		if tax_template:
			tax_details = frappe.get_all(
				"Item Tax",
				filters={"parent": tax_template},
				fields=["item_tax_template", "tax_category"]
			)
			for tax in tax_details:
				item.append("taxes", {
					"item_tax_template": tax.get("item_tax_template"),
					"tax_category": tax.get("tax_category"),
				})

		item.save()
		frappe.db.commit()
		self.item_code_prod = item.name

	@frappe.whitelist()
	def change_status(self, status):
		if status == "Closed" or status == "Completed":
			frappe.db.sql(""" UPDATE `tabProduction` SET last_status=%s WHERE name=%s """,(self.status, self.name))
			frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s """,(status, self.name))
			frappe.db.commit()
		elif status == "Open":
			frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s """, (self.last_status, self.name))
			frappe.db.commit()

		if status == "Completed":
			self.get_service_records()

	@frappe.whitelist()
	def get_service_records(self):
		estimation_ = ""
		estimation = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name= %s""", self.name, as_dict=1)
		if len(estimation) > 0:
			estimation_ = estimation[0].estimation
			frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s""",
						  ("Completed", estimation_))

		inspections = frappe.db.sql(""" SELECT * FROM `tabInspection Table` WHERE parent=%s """, estimation_,
									as_dict=1)
		for i in inspections:
			frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s""",
						  ("Completed", i.inspection))

		srn = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE name=%s """, estimation_, as_dict=1)
		if len(srn) > 0:
			srn_ = srn[0].service_receipt_note
			frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s""",
						  ("Completed", srn_))
		frappe.db.commit()

	@frappe.whitelist()
	def on_update_after_submit(self):
		for i in self.raw_material:
			if i.production:
				get_qty = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s""", i.production, as_dict=1)
				get_qty_total = frappe.db.sql(""" SELECT SUM(qty_raw_material) as qty_raw_material FROM `tabRaw Material` WHERE production=%s """, i.production, as_dict=1)
				if get_qty[0].qty == get_qty_total[0].qty_raw_material:
					frappe.db.sql(""" UPDATE `tabProduction` SET status=%s, last_status=%s WHERE name=%s""", ("Completed",get_qty[0].status,i.production))
					frappe.db.commit()
				else:
					frappe.db.sql(""" UPDATE `tabProduction` SET status=%s, last_status=%s WHERE name=%s""", ("Linked",get_qty[0].status,i.production))
					frappe.db.commit()

	@frappe.whitelist()
	def change_production_status(self, production):
		raw_material = frappe.db.sql(""" SELECT * FROM `tabRaw Material` WHERE name=%s""",production, as_dict=1)
		if len(raw_material) > 0 and raw_material[0].production:

			frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Deliver and Bill", raw_material[0].production))
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
				get_qty = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s""", i.production, as_dict=1)
				get_qty_total = frappe.db.sql(""" SELECT SUM(qty_raw_material) as qty_raw_material FROM `tabRaw Material` WHERE production=%s """, i.production, as_dict=1)
				if get_qty[0].qty == get_qty_total[0].qty_raw_material:
					frappe.db.sql(""" UPDATE `tabProduction` SET status=%s, last_status=%s WHERE name=%s""", ("Completed",get_qty[0].status,i.production))
					frappe.db.commit()
				else:
					frappe.db.sql(""" UPDATE `tabProduction` SET status=%s, last_status=%s WHERE name=%s""", ("Linked",get_qty[0].status,i.production))
					frappe.db.commit()

	@frappe.whitelist()
	def set_available_qty(self):
		time = frappe.utils.now_datetime().time()
		date = frappe.utils.now_datetime().date()
		for d in self.get('raw_material'):
			previous_sle = get_previous_sle({
				"item_code": d.item_code,
				"warehouse": d.warehouse,
				"posting_date": date,
				"posting_time": time
			})
			# get actual stock at source warehouse
			d.available_qty = previous_sle.get("qty_after_transaction") or 0

	@frappe.whitelist()
	def validate(self):
		if self.type == "Service":
			self.series = "CS-0"
		self.validate_raw_material_batch()
		self.update_total_average_amount()
		
		# Calculate total selling rate during validation
		self.calculate_total_selling_rate()
		
	def validate_raw_material_batch(self):
		for row in self.raw_material:
			item = frappe.get_doc('Item', row.item_code)
			if item.has_batch_no and not row.batch:
				frappe.throw(_('Item "{}" is a batch item. Please select a batch.').format(item.item_code))
	def update_total_average_amount(self):
		total_from_raw_materials = 0
		for row in self.raw_material:
			total_from_raw_materials += flt(row.total or 0)  # Changed from average_rate to total
			
		scoop_total = flt(self.scoop_of_work_total or 0)
		self.average_price = total_from_raw_materials + scoop_total
		self.total_average_amount = self.average_price

	@frappe.whitelist()
	def check_raw_materials(self):
		for i in self.raw_material:
			if i.available_qty == 0:
				return False, i.item_code
		return True, ""

	@frappe.whitelist()
	def generate_se(self):
		print("SULOD SA METHOOOOOOOOOOOOOOD")
		check,item_code = self.check_raw_materials()
		allow_negative_stock = cint(frappe.db.get_value("Stock Settings", None, "allow_negative_stock"))
		if check or (not check and allow_negative_stock) or self.type == "Disassemble":
			print("STOCK ENTRRRRRRRRYYYYYYYYYYYYYYYYYYY")
			doc_se = {
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture" if self.type == "Assemble" or self.type == "Service"  else "Material Issue" if self.type == "Re-Service" else"Repack",
				"items": self.get_manufacture_se_items() if self.type == "Assemble" or self.type == "Service"  else self.get_material_issue_se_items() if self.type == "Re-Service" else self.get_repack_se_items(),
				"production": self.name,
				"company": self.company,
				"additional_costs": self.get_additional_costs()
			}
			frappe.get_doc(doc_se).insert(ignore_permissions=1).submit()


			if self.type == "Re-Service":
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("Completed", self.name))
				frappe.db.commit()
			else:
				frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
							  ("To Deliver and Bill", self.name))
				frappe.db.commit()
			return ""
		else:
			frappe.throw("Item " + item_code + " Has no available stock")

	@frappe.whitelist()
	def generate_finish_good_se(self):
		# Calculate basic_amount
		basic_amount = flt(self.total_cost_rate) * flt(self.qty)
		
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
				'basic_rate': self.total_cost_rate,
				'basic_amount': basic_amount, 
				'cost_center': self.cost_center,
				"set_basic_rate_manually": 1,
				'custom_production_id': self.name,
			}],
		}
		frappe.get_doc(doc_se1).insert(ignore_permissions=1).submit()

	@frappe.whitelist()
	def get_additional_costs(self):
		costs = []
		settings = frappe.get_doc("Production Settings")

		for row in settings.company_expense_ledger:
			if row.company == self.company:
				costs.append({
					"expense_account": row.expense_ledger_account,
					"description": "Company Expense Ledger",
					"amount": self.scoop_of_work_total
				})

		return costs


	@frappe.whitelist()
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

	@frappe.whitelist()
	def generate_si(self):
		if self.input_qty > self.qty_for_sidn:
			frappe.throw("Maximum qty that can be generated is " + str(self.qty))
		default_tax = frappe.db.sql(""" SELECT * FROM `tabSales Taxes and Charges Template` WHERE is_default = 1""",as_dict=1)
		doc_si = {
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"items": self.get_si_items("SI", self.input_qty),
			"production": self.get_production_items(self.input_qty),
		}
		if len(default_tax) > 0:
			doc_si['taxes_and_charges'] = default_tax[0].name

		si = frappe.get_doc(doc_si)
		si.insert(ignore_permissions=1)
		return si.name
	
	@frappe.whitelist()
	def generate_so(self):
		if self.input_qty > self.qty_for_sidn:
			frappe.throw("Maximum qty that can be generated is " + str(self.qty))
		default_tax = frappe.db.sql(""" SELECT * FROM `tabSales Taxes and Charges Template` WHERE is_default = 1""",as_dict=1)
		doc_so = {
			"doctype": "Sales Order",
			"customer": self.customer,
			"delivery_date":self.delivery_date,
			"items": self.get_si_items("SI", self.input_qty),
			"custom_production": self.get_production_items(self.input_qty),
		}
		if len(default_tax) > 0:
			doc_so['taxes_and_charges'] = default_tax[0].name

		so = frappe.get_doc(doc_so)
		so.insert(ignore_permissions=1)
		return so.name

	@frappe.whitelist()
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

	@frappe.whitelist()
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

	@frappe.whitelist()
	def get_manufacture_se_items(self):
		items = []

		for item in self.raw_material:
			items.append({
				'item_code': item.item_code,
				's_warehouse': item.warehouse,
				'qty': item.qty_raw_material,
				'uom': item.umo,
				'basic_rate': item.rate_raw_material,
				'cost_center': item.cost_center,
				"batch_no": item.batch,
				"serial_and_batch_bundle": self.update_serial_and_batch_bundle(item),
				'custom_production_id': self.name, 
			})

		# Calculate basic_amount for the finished item
		basic_amount = flt(self.total_cost_rate) * flt(self.qty)
		
		items.append({
			'item_code': self.item_code_prod,
			't_warehouse': self.warehouse,
			'qty': self.qty,
			'uom': self.umo,
			'basic_rate': self.total_cost_rate,
			'basic_amount': basic_amount,  
			'cost_center': self.cost_center,
			'is_finished_item': 1,
			"set_basic_rate_manually": 1,
			'custom_production_id': self.name, 
		})
		return items
	
	@frappe.whitelist()
	def update_serial_and_batch_bundle(self, item):
		print(item.item_code)
		if item.batch:
			serial_and_batch_bundle = frappe.new_doc("Serial and Batch Bundle")
			serial_and_batch_bundle.item_code = item.item_code
			serial_and_batch_bundle.warehouse = item.warehouse
			serial_and_batch_bundle.type_of_transaction = "Outward" if self.type else "Inward"
			serial_and_batch_bundle.voucher_type = "Stock Entry"
			serial_and_batch_bundle.company = self.company
			serial_and_batch_bundle.posting_date = self.posting_date
			serial_and_batch_bundle.posting_time = self.posting_time
			serial_and_batch_bundle.append("entries",{
				"batch_no":item.batch,
				"warehouse":item.warehouse,
				"qty":item.qty_raw_material
			})
			serial_and_batch_bundle.save(ignore_permissions=True)
			return serial_and_batch_bundle.name
			
	@frappe.whitelist()
	def get_material_issue_se_items(self):
		items = []

		for item in self.raw_material:
			batch_no = None
			if item.batch:
				batch_no = self.update_serial_and_batch_bundle(item)

			items.append({
				'item_code': item.item_code,
				's_warehouse': item.warehouse,
				'qty': item.qty_raw_material,
				'uom': item.umo,
				'basic_rate': item.rate_raw_material,
				'cost_center': item.cost_center,
				"batch_no": item.batch,
				"serial_and_batch_bundle": batch_no,
				'custom_production_id': self.name,
			})
		return items

	@frappe.whitelist()
	def get_repack_se_items(self):
		items = []

		for item in self.raw_material:
			if item.available_qty > 0 or self.type == "Disassemble":
				# Calculate basic_amount for raw material items going to target warehouse
				basic_amount = flt(self.total_cost_rate) * flt(self.qty)
				
				items.append({
					'item_code': item.item_code,
					't_warehouse': item.warehouse,
					'qty': item.qty_raw_material,
					'uom': self.umo,
					'basic_rate': self.total_cost_rate,
					'basic_amount': basic_amount,  
					'cost_center': item.cost_center,
					"batch_no": item.batch,
					"set_basic_rate_manually": 1,
					"serial_and_batch_bundle": self.update_serial_and_batch_bundle(item),
					'custom_production_id': self.name,
				})

		items.append({
			'item_code': self.item_code_prod,
			's_warehouse': self.warehouse,
			'qty': self.qty,
			'uom': self.umo,
			'basic_rate': self.rate,
			'cost_center': self.cost_center,
			'custom_production_id': self.name,
		})
		return items

	@frappe.whitelist()
	def get_si_items(self, type, qty):

		obj = {
			'item_code': self.item_code_prod,
			'item_name': self.get_item_value("item_name"),
			'description': self.get_item_value("description"),
			'qty': qty,
			'uom': "Nos",
			'rate': self.invoice_rate,
			'cost_center': self.cost_center,
			'income_account': self.income_account
		}
		if type == "DN":
			obj["warehouse"] = self.warehouse
		return [obj]

	@frappe.whitelist()
	def get_production_items(self, qty):
		return [{
			'reference': self.name,
			'qty': qty,
			'rate': self.invoice_rate,
			'amount': self.invoice_rate * qty,

		}]

	# @frappe.whitelist()
	# def get_sales_man(self):
	# 	return [{
	# 		'sales_man': self.sales_man,
	# 		'reference': self.name,
	# 	}]

	@frappe.whitelist()
	def get_item_value(self, field):
		items = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, self.item_code_prod, as_dict=1)
		return items[0][field]

@frappe.whitelist()
def get_available_qty(production):
	get_qty = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s""", production, as_dict=1)
	get_qty_total = frappe.db.sql(
		""" SELECT SUM(RM.qty_raw_material) as qty_raw_material FROM `tabProduction` AS P INNER JOIN `tabRaw Material` AS RM ON RM.parent = P.name and RM.production=%s WHERE P.docstatus=1 """,
		production, as_dict=1)
	print(get_qty_total)
	return get_qty[0].qty - get_qty_total[0].qty_raw_material if get_qty_total[0].qty_raw_material else get_qty[0].qty

@frappe.whitelist()
def get_rate(item_code, warehouse, based_on,price_list):
	time = frappe.utils.now_datetime().time()
	date = frappe.utils.now_datetime().date()
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
		condition += " and selling = 1 and price_list='{0}'".format('Standard Selling')

	query = """ SELECT * FROM `tabItem Price` WHERE item_code=%s {0} ORDER BY valid_from DESC LIMIT 1""".format(condition)

	item_price = frappe.db.sql(query,item_code, as_dict=1)
	rate = item_price[0].price_list_rate if len(item_price) > 0 else 0
	print(based_on)
	if based_on == "Valuation Rate":
		print("WALA DIR")
		item_record = frappe.db.sql(
			""" SELECT * FROM `tabItem` WHERE item_code=%s""",
			item_code, as_dict=1)
		rate = item_record[0].valuation_rate if len(item_record) > 0 else 0
	if based_on == "Last Purchase Rate":
		print("WALA DIR")
		item_record = frappe.db.sql(
			""" SELECT * FROM `tabItem` WHERE item_code=%s""",
			item_code, as_dict=1)
		rate = item_record[0].last_purchase_rate if len(item_record) > 0 else 0
	return rate, balance

@frappe.whitelist()
def get_uom(item_code):
	item = frappe.db.sql(
		""" SELECT * FROM `tabItem` WHERE name=%s""",
		item_code, as_dict=1)

	return item[0].stock_uom, item[0].item_name

# @frappe.whitelist()
# def get_address(customer):
# 	address = frappe.db.sql(""" 
#  						SELECT
#  						 	A.name,
#  							A.address_line1, 
# 							A.city, 
# 							A.county ,
# 							A.state,
# 							A.country,
# 							A.pincode
# 						FROM `tabAddress` AS A 
#  						INNER JOIN `tabDynamic Link` AS DL 
#  						ON DL.link_doctype=%s and DL.link_name=%s and DL.parent = A.name
#  						WHERE A.is_primary_address=1  """,("Customer", customer), as_dict=1)
# 	return address[0] if len(address) > 0 else {}

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

	so_query = """ 
		SELECT SIP.qty as qty, SO.status FROM `tabSales Order` AS SO 
		INNER JOIN `tabSales Invoice Production` AS SIP ON SO.name = SIP.parent 
		WHERE SIP.reference=%s and SIP.parenttype=%s and SO.docstatus = 1 and SO.status!='Cancelled'
		"""
	so = frappe.db.sql(so_query, (name, "Sales Order"), as_dict=1)
	si_query = """ 
		SELECT SIP.qty as qty, SI.status FROM `tabSales Invoice` AS SI 
		INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
		WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1 and SI.status!='Cancelled'
		"""
	si = frappe.db.sql(si_query, (name, "Sales Invoice"), as_dict=1)
	dn_query = """ 
			SELECT SIP.qty as qty, DN.status FROM `tabDelivery Note` AS DN 
			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1 and DN.status!='Cancelled'
			"""
	dn = frappe.db.sql(dn_query, (name, "Delivery Note"), as_dict=1)

	total_qty = 0
	if len(so)> 0:
		for k in so:
			total_qty += k.qty
		return float(qty) - float(total_qty)
	if len(si) > len(dn):
		for i in si:
			total_qty += i.qty

	elif len(dn) > len(si):
		for d in dn:
			total_qty += d.qty
	elif len(dn) == len(si):
		for d in dn:
			total_qty += d.qty
	# print("TOTALALLL")
	# print(total_qty)
	return float(qty) - float(total_qty)



@frappe.whitelist()
def change_status(name):
	frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Partially Delivered", name))
	frappe.db.commit()
	return 1

@frappe.whitelist()
def get_valuation_rate(item_code):
	item = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE item_code=%s""", (item_code),as_dict=1)
	return item[0].valuation_rate if len(item) > 0 else 0

@frappe.whitelist()
def compute_selling_price(raw_materials):
	import json
	selling_price_total = 0
	raw_material = json.loads(raw_materials)
	for i in raw_material:
		warehouse = i['warehouse'] if 'warehouse' in i and i['warehouse'] else "",
		if 'item_code' in i:
			selling_price = get_rate(i['item_code'],warehouse,"Price List", "Standard Selling")

			selling_price_total += (selling_price[0] * i['qty_raw_material'])
	return selling_price_total


@frappe.whitelist()
def selling_price_list(raw_materials):
	import json
	array_selling = []
	raw_material = json.loads(raw_materials)

	for i in raw_material:
		warehouse = i['warehouse'] if 'warehouse' in i and i['warehouse'] else "",
		if 'item_code' in i:
			selling_price = get_rate(i['item_code'],warehouse,"Price List", "Standard Selling")

			array_selling.append({
				"item_name": i['item_name'],
				"qty_raw_material": i['qty_raw_material'],
				"rate_raw_material": selling_price[0] * i['qty_raw_material']
			})
	return array_selling

@frappe.whitelist()
def update_dispatch_address(customer):
		
	address_name = frappe.db.get_value('Dynamic Link', {
		'link_doctype': 'Customer',
		'link_name': customer,
		'parenttype': 'Address'
		}, 'parent')
	
	return address_name


@frappe.whitelist()
def create_delivery_note(source_name, target_doc=None):
    def set_missing_values(source, target):
        """Set default values for fields in the Delivery Note."""
        target.append("items", {
            "item_code": source.item_code_prod,  
            "qty": source.qty,  
            "uom": source.umo,
			"stock_uom": source.umo,    
            "item_name": source.item_name, 
            "rate": source.invoice_rate 
        })

    doclist = get_mapped_doc(
        "Production",
        source_name,
        {
            "Production": {
                "doctype": "Delivery Note",
                "field_map": {
                    "customer": "customer", 
                    "company": "company",  
                    "posting_date": "posting_date",  
					"name":"custom_production_id"
                },
				"field_no_map": [
                    "cost_center"  
                ]
            }
        },
        target_doc,
        set_missing_values
    )

    return doclist



@frappe.whitelist()
def create_sales_invoice(source_name, target_doc=None):
    doclist = get_mapped_doc(
        "Production", 
        source_name, 
        {
            "Production": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "customer": "customer",
                    "company": "company",
                    "custom_production_id": "name",
                    "posting_date": "posting_date"
                },
                "field_no_map": [
                    "cost_center"  
                ]
            },
            "Raw Material": {
                "doctype": "Sales Invoice Item"
            }
        },
        target_doc
    )

    return doclist








@frappe.whitelist()
def get_role():
    doc = frappe.db.get_value("Production Settings", None, "ignore_permission")
    return doc


@frappe.whitelist()
def get_estimation_raw_material(estimation_id):
    try:
        estimation = frappe.get_doc('Estimation', estimation_id)
        raw_material_data = []
        
        for row in estimation.raw_material:
            raw_material_data.append({
                'item_code': row.item_code,
                'item_name': row.item_name,
                'warehouse': row.warehouse,
                'available_qty': row.available_qty,
                'production': row.production,
                'batch': row.batch,
                'umo': row.umo,
                'qty_raw_material': row.qty_raw_material,
                'rate_raw_material': row.rate_raw_material,
                'amount_raw_material': row.amount_raw_material,
                'cost_center': row.cost_center
            })
        
        return raw_material_data
    except frappe.DoesNotExistError:
        frappe.throw(f"Estimation {estimation_id} does not exist.")
    except Exception as e:
        frappe.throw(f"An error occurred while fetching data: {str(e)}")




@frappe.whitelist()
def get_customer_name(customer):
    if customer:
        customer_name = frappe.db.get_value("Customer", customer, "customer_name")
        return customer_name
    return None

@frappe.whitelist()
def get_valuation_rate_from_sle(item_code, warehouse):
    """
    Standalone function to get valuation rate from Stock Ledger Entry
    """
    try:
        # Get the latest stock ledger entry with valuation rate
        sle = frappe.db.sql("""
            SELECT 
                valuation_rate,
                stock_value,
                qty_after_transaction,
                posting_date,
                posting_time
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s 
            AND warehouse = %s 
            AND is_cancelled = 0
            AND docstatus < 2
            AND valuation_rate IS NOT NULL
            AND valuation_rate > 0
            ORDER BY posting_date DESC, posting_time DESC, creation DESC
            LIMIT 1
        """, (item_code, warehouse), as_dict=1)
        
        if sle and len(sle) > 0:
            return float(sle[0].valuation_rate)
        else:
            # Fallback to item valuation rate
            item_valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate")
            return float(item_valuation_rate) if item_valuation_rate else 0.0
            
    except Exception as e:
        frappe.log_error(f"Error in get_valuation_rate_from_sle: {str(e)}")
        return 0.0

@frappe.whitelist()
def get_total_selling_rate(production_name):
    """Standalone function to calculate total selling rate"""
    doc = frappe.get_doc("Production", production_name)
    total = 0
    for row in doc.item_selling_price_list:
        if row.selling_rate:
            total += flt(row.selling_rate)
    return total


# Add this method to your Production class in production.py

@frappe.whitelist()
def get_estimation_scoop_of_work(estimation_id):
    """
    Fetch only scoop_of_work table data from the selected Estimation document
    """
    try:
        estimation = frappe.get_doc('Estimation', estimation_id)
        scoop_of_work_data = []
        
        for row in estimation.scoop_of_work:
            scoop_of_work_data.append({
                'work_name': row.work_name,
                'estimated_date': row.estimated_date,
                'cost': row.cost,
                'status': getattr(row, 'status', 'Pending')  # Default to 'Pending' if status field doesn't exist
            })
        
        return scoop_of_work_data
        
    except frappe.DoesNotExistError:
        frappe.throw(f"Estimation {estimation_id} does not exist.")
    except Exception as e:
        frappe.throw(f"An error occurred while fetching scoop of work data: {str(e)}")

@frappe.whitelist()
def calculate_total_cost_rate(self):
    """Calculate total cost rate from raw material total field"""
    total_cost = 0
    for row in self.raw_material:
        if row.total:
            total_cost += flt(row.total)
    
    self.total_cost_rate = total_cost
    return total_cost