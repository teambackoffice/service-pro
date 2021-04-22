# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from erpnext.stock.stock_ledger import get_previous_sle

class SiteJobReport(Document):


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