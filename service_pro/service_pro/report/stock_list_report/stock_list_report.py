# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.stock.doctype.item.item import get_last_purchase_details
from frappe.utils import flt
from erpnext.stock.stock_ledger import get_previous_sle
from datetime import *
def get_columns():
	return [
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": "100"},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data","width": "300"},
		{"label": "Available Stock", "fieldname": "available_stock", "fieldtype": "Float", "width": "150"},
		{"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Float", "width": "120"},
		{"label": "Last Purchase Rate", "fieldname": "last_purchase_rate", "fieldtype": "Float","width": "150"},
		{"label": "Selling Rate", "fieldname": "selling_rate", "fieldtype": "Float", "width": "100"},
	]

def execute(filters=None):
	columns, data = get_columns(), []
	date = datetime.now().date()
	if filters.get("date"):
		date = filters.get("date")
	condition = ""
	if filters.get("item_group"):
		condition += " and item_group='{0}' ".format(filters.get("item_group"))
	query = """ SELECT * FROM `tabItem` WHERE disabled=0 {0}""".format(condition)
	items = frappe.db.sql(query, as_dict=1)

	for item in items:
		item_defaults = frappe.db.sql(""" SELECT * FROM `tabItem Default` WHERE parent=%s and idx=1 """, item.name, as_dict=1)
		item_price = frappe.db.sql(""" SELECT * FROM `tabItem Price` WHERE item_code=%s and selling=1 ORDER BY creation DESC LIMIT 1 """, item.item_code, as_dict=1)

		obj = {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"valuation_rate": item.valuation_rate,
			"selling_rate": item_price[0].price_list_rate if len(item_price) > 0 else 0,
			"last_purchase_rate": get_last_purchase_rate(item.item_code),
			"available_stock": get_previous_stock(item.item_code, item_defaults[0].default_warehouse if len(item_defaults) > 0 else "", date),
		}
		if filters.get("ignore_zero_stock") and not filters.get("ignore_negative_stock"):
			if get_previous_stock(item.item_code, item_defaults[0].default_warehouse if len(item_defaults) > 0 else "", date) != 0:
				data.append(obj)

		elif filters.get("ignore_negative_stock") and not filters.get("ignore_zero_stock"):
			if get_previous_stock(item.item_code, item_defaults[0].default_warehouse if len(item_defaults) > 0 else "",
								  date) >= 0:
				data.append(obj)

		elif filters.get("ignore_negative_stock") and filters.get("ignore_zero_stock"):
			if get_previous_stock(item.item_code, item_defaults[0].default_warehouse if len(item_defaults) > 0 else "",
								  date) > 0:
				data.append(obj)
		else:
			data.append(obj)
	print(columns)
	print(data)
	return columns, data

def get_previous_stock(item_code, warehouse, date):
	previous_sle = get_previous_sle({
		"item_code": item_code,
		"warehouse": warehouse,
		"posting_date": date,
		"posting_time": "11:59:59"
	})
	return previous_sle.get("qty_after_transaction") or 0

def get_last_purchase_rate(item_code):
		if item_code:
			last_purchase_details = get_last_purchase_details(item_code)
			if last_purchase_details:
				return last_purchase_details['base_rate'] * 1.0

			else:

				item_last_purchase_rate = frappe.get_cached_value("Item", item_code, "last_purchase_rate")
				if item_last_purchase_rate:
					return item_last_purchase_rate