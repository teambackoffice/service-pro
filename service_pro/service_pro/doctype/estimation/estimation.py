# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import cint, flt
from datetime import datetime
class Estimation(Document):
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
def get_dimensions():
	rod_dia, r_length, tube_size, t_length = [],[],[],[]

	dimensions = frappe.get_single("Cylinder Dimensions").__dict__

	for rod in dimensions['rod_dia']:
		rod_dia.append(rod.dimension)

	for r in dimensions['r_length']:
		r_length.append(r.dimension)

	for tube in dimensions['tube_size']:
		tube_size.append(tube.dimension)

	for t in dimensions['t_length']:
		t_length.append(t.dimension)

	return rod_dia, r_length, tube_size, t_length

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
