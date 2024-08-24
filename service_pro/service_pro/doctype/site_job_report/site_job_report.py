# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from erpnext.stock.stock_ledger import get_previous_sle

class SiteJobReport(Document):
	@frappe.whitelist()
	def get_defaults(self):
		if self.company:
			defaults = {
				"item_naming_series": frappe.db.get_value("Production Settings", None, "item_naming_series") or "",
				"item_group": frappe.db.get_value("Production Settings", None, "item_group") or "",
				# "finish_good_cost_center": frappe.db.get_value("Production Settings", None, "finish_good_cost_center") or "",
				"credit_note_user_role": frappe.db.get_value("Production Settings", None,
															 "credit_note_user_role") or "",
				"debit_note_user_role": frappe.db.get_value("Production Settings", None, "debit_note_user_role") or "",
				# "income_account": frappe.db.get_value("Production Settings", None, "income_account") or "",
				# "finish_good_warehouse": frappe.db.get_value("Production Settings", None, "finish_good_warehouse") or "",
				"mandatory_additional_cost_in_production": frappe.db.get_value("Production Settings", None,
																			   "mandatory_additional_cost_in_production") or 0,
				"enable_sales_order_validation": frappe.db.get_value("Production Settings", None,
																	 "enable_sales_order_validation") or 0,
				"automatically_create_jv": frappe.db.get_value("Production Settings", None,
															   "automatically_create_jv") or 0,
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
				data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.company,
									 as_dict=1)
				if len(data) > 0:
					defaults[data[0].parentfield] = data[0]

			# self.warehouse = defaults[
			# 	'finish_good_defaults'].finish_good_warehouse if 'finish_good_defaults' in defaults else ""
			# self.cost_center = defaults[
			# 	'finish_good_defaults'].finish_good_cost_center if 'finish_good_defaults' in defaults else ""
			# self.income_account = defaults[
			# 	'finish_good_defaults'].income_account if 'finish_good_defaults' in defaults else ""
			self.rate_of_materials_based_on = defaults[
				'rate_of_materials_based_on'] if 'rate_of_materials_based_on' in defaults else ""
			self.price_list = defaults['price_list'] if 'price_list' in defaults else ""
			return defaults
	def on_trash(self):
		if self.svrj_row_name:
			frappe.db.sql(""" UPDATE `tabSite Visit Report Jobs` SET job_card_number=%s WHERE name=%s""",("", self.svrj_row_name))
			frappe.db.commit()

	def on_cancel(self):
		if self.svrj_row_name:
			frappe.db.sql(""" UPDATE `tabSite Visit Report Jobs` SET job_card_number=%s WHERE name=%s""",("", self.svrj_row_name))
			frappe.db.commit()

	@frappe.whitelist()
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
def get_available_qty(production):
	get_qty = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s""", production, as_dict=1)
	get_qty_total = frappe.db.sql(
		""" SELECT SUM(RM.qty_raw_material) as qty_raw_material FROM `tabProduction` AS P INNER JOIN `tabRaw Material` AS RM ON RM.parent = P.name and RM.production=%s WHERE P.docstatus=1 """,
		production, as_dict=1)
	print(get_qty_total)
	return get_qty[0].qty - get_qty_total[0].qty_raw_material if get_qty_total[0].qty_raw_material else get_qty[0].qty


@frappe.whitelist()
def permanent_submit(name):
	frappe.db.sql(""" UPDATE `tabSite Job Report` SET permanent_submit=1, sjr_status='Completed', status='Completed' WHERE name=%s""", name)
	frappe.db.commit()