# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance

class Estimation(Document):
	pass

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
def get_rate(item_code, warehouse):
	item_price = frappe.db.sql(""" SELECT * FROM `tabItem Price` WHERE item_code=%s and selling=1 ORDER BY valid_from DESC LIMIT 1""", item_code,as_dict=1)
	if warehouse:
		print(get_stock_balance(item_code,warehouse))

	return item_price[0].price_list_rate if len(item_price) > 0 else 0,get_stock_balance(item_code,warehouse) if warehouse else 0