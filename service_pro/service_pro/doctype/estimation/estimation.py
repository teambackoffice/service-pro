# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe import _
from frappe.model.document import Document
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import cint, flt
from datetime import datetime
class Estimation(Document):
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
	@frappe.whitelist()
	def change_status(self, status):

		frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s """,(status, self.name))
		frappe.db.commit()
	def validate(self):
		for raw in self.raw_material:
			if not raw.cost_center:
				frappe.throw("Please Input Valid Cost Center in Raw Material row " + str(raw.idx))
	def on_submit(self):
		for i in self.inspections:
			self.check_status("To Production", i.inspection)

	def on_cancel(self):
		for i in self.inspections:
			self.check_status("To Estimation", i.inspection)

	@frappe.whitelist()
	def check_status(self,status, name):
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s """,
					  (status, name))

		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s """,
					  (status, self.receipt_note))

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
		item_price = frappe.db.sql(
			""" SELECT * FROM `tabItem` WHERE item_code=%s""",
			item_code, as_dict=1)
		rate = item_price[0].valuation_rate if len(item_price) > 0 else 0

	return rate, balance

@frappe.whitelist()
def calculate_cost(doc, method):
    total_hours = 0
    total_machine_cost = 0
    total_worker_cost = 0

    for row in doc.workshop_details:
        # Machine cost calculation
        if row.machine_name:
            cost_rate = frappe.db.get_value("Machine", row.machine_name, "cost_rate") or 0
            row.total_machine_cost = cost_rate * row.hrs

        # Worker cost calculation
        if row.worker:
            worker_rate = frappe.db.get_value("Worker", row.worker, "worker_per_hour_cost") or 0
            row.total_worker_cost = worker_rate * row.hrs

        # Cost Amount = total_machine_cost + total_worker_cost
        row.cost_amount = (row.total_machine_cost or 0) + (row.total_worker_cost or 0)

        # Update totals
        total_hours += row.hrs or 0
        total_machine_cost += row.total_machine_cost or 0
        total_worker_cost += row.total_worker_cost or 0

    doc.total_machine_hours = total_hours
    doc.total_cost_amount = total_machine_cost
  


@frappe.whitelist()
def create_production(source_name, target_doc=None):
    

    doclist = get_mapped_doc(
    "Estimation",
    source_name,
    {
        "Estimation": {
            "doctype": "Quotation",
            "field_map": {
				"name": "custom_estimation", 
				"customer": "party_name",
            }
        },
        # "Scoop of Work": {
        #     "doctype": "Scoop of Work",
        #     "field_map": {
            
        #     }
        #     }

    },
    target_doc
    )

    return doclist






