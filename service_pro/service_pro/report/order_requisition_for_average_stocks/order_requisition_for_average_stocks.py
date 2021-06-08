# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.stock.stock_ledger import get_previous_sle

def get_columns(filters):
	columns = [
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link","options": "Item", "width": "100"}
	]
	if filters.get("average_stock") == "January-June":
		columns.append({"label": "Jan", "fieldname": "jan", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Feb", "fieldname": "feb", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Mar", "fieldname": "mar", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Apr", "fieldname": "apr", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "May", "fieldname": "may", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "June", "fieldname": "june", "fieldtype": "Float", "width": "100"})

	if filters.get("average_stock") == "July-December":
		columns.append({"label": "July", "fieldname": "july", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Aug", "fieldname": "aug", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Sept", "fieldname": "sept", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Oct", "fieldname": "oct", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Nov", "fieldname": "nov", "fieldtype": "Float", "width": "100"})
		columns.append({"label": "Dec", "fieldname": "dec", "fieldtype": "Float", "width": "100"})

	columns.append({"label": "Average Sale Per Month", "fieldname": "average_sale_per_month", "fieldtype": "Float", "width": "200"})
	columns.append({"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": "150"})
	columns.append({"label": "Average Sell Stock", "fieldname": "average_sell_stock", "fieldtype": "Float", "width": "200"})
	columns.append({"label": "Stock Position", "fieldname": "stock_position", "fieldtype": "Float", "width": "150"})
	columns.append({"label": "Stock Month", "fieldname": "stock_month", "fieldtype": "Float", "width": "150"})
	return columns
def execute(filters=None):
	columns, data = get_columns(filters), []
	time = frappe.utils.now_datetime().time()
	date = frappe.utils.now_datetime().date()
	average_stock_dates = get_dates(filters.get("average_stock"))
	item_group = filters.get("item_group")
	item = filters.get("item")
	condition = ""
	if item_group:
		condition += " and item_group='{0}'".format(item_group)
	if item:
		condition += " and name='{0}'".format(item)
	query = """ SELECT * FROM `tabItem` WHERE disabled=0 {0}""".format(condition)
	items = frappe.db.sql(query, as_dict=1)
	for item in items:
		query = """ SELECT *
					FROM `tabStock Ledger Entry` 
					WHERE item_code='{0}' and actual_qty < 0""".format(item.name)
		sle_check = frappe.db.sql(query, as_dict=1)
		if len(sle_check) > 0:
			obj = {
				"item_code": item.name,
			}
			get_sle(item.name, average_stock_dates,obj)
			obj['current_stock'] = get_previous_sle({
				"item_code": item.name,
				"posting_date": date,
				"posting_time": time
			}).get("qty_after_transaction") or 0

			obj['stock_position'] = obj['current_stock'] - obj['average_sell_stock']
			obj['stock_month'] = obj['current_stock'] / (obj['average_sale_per_month'] if obj['average_sale_per_month'] > 0 else 1 )
			data.append(obj)

	print(data)
	return columns, data


def get_dates(average_stock):
	fiscal_year = frappe.get_single("Global Defaults").__dict__['current_fiscal_year']
	if average_stock == "January-June":
		return [
			{"from_date": fiscal_year + "-01" + "-01", "to_date": fiscal_year  + "-01" + "-31", "month": "jan"},
			{"from_date": fiscal_year + "-02" + "-01", "to_date": fiscal_year  + "-02" + "-28", "month": "feb"},
			{"from_date": fiscal_year + "-03" + "-01", "to_date": fiscal_year  + "-03" + "-31", "month": "mar"},
			{"from_date": fiscal_year + "-04" + "-01", "to_date": fiscal_year  + "-04" + "-30", "month": "apr"},
			{"from_date": fiscal_year + "-05" + "-01", "to_date": fiscal_year  + "-05" + "-31", "month": "may"},
			{"from_date": fiscal_year + "-06" + "-01", "to_date": fiscal_year  + "-06" + "-30", "month": "june"},
		]

	if average_stock == "July-December":
		return [
			{"from_date": fiscal_year + "-07" + "-01", "to_date": fiscal_year + "-07" + "-31", "month": "july"},
			{"from_date": fiscal_year + "-08" + "-01", "to_date": fiscal_year + "-08" + "-31", "month": "aug"},
			{"from_date": fiscal_year + "-09" + "-01", "to_date": fiscal_year + "-09" + "-30", "month": "sept"},
			{"from_date": fiscal_year + "-10" + "-01", "to_date": fiscal_year + "-10" + "-31", "month": "oct"},
			{"from_date": fiscal_year + "-11" + "-01", "to_date": fiscal_year + "-11" + "-30", "month": "nov"},
			{"from_date": fiscal_year + "-12" + "-01", "to_date": fiscal_year + "-12" + "-31", "month": "dec"},
		]


def get_sle(item_code,average_stock_dates,item_code_sums):
	average_stock = 0
	for date in average_stock_dates:
		query = """ SELECT SUM(actual_qty) as actual_qty_sum
					FROM `tabStock Ledger Entry` 
					WHERE item_code='{0}' and actual_qty < 0 and posting_date BETWEEN '{1}' and '{2}'""".format(item_code, date['from_date'],date['to_date'])
		sle = frappe.db.sql(query,as_dict=1)
		print(item_code)
		item_code_sums[date['month']] =  abs(sle[0].actual_qty_sum) if sle[0].actual_qty_sum else 0
		average_stock += abs(sle[0].actual_qty_sum) if sle[0].actual_qty_sum else 0
	item_code_sums['average_sale_per_month'] = average_stock / 6
	item_code_sums['average_sell_stock'] = (average_stock / 6) * 4
	return item_code_sums