# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def get_columns():
	return [
			{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "100"},
			{"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": "110"},
			{"label": "VAT Number", "fieldname": "vat_number", "fieldtype": "Data", "width": "120"},
			{"label": "Invoice Number", "fieldname": "name", "fieldtype": "Data", "width": "130"},
			{"label": "Amount", "fieldname": "total", "fieldtype": "Currency", "width": "130"},
			{"label": "Discount", "fieldname": "discount_amount", "fieldtype": "Currency","width": "100"},
			{"label": "VAT", "fieldname": "total_taxes_and_charges", "fieldtype": "Currency","width": "100"},
			{"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency","width": "100"},
		]

def execute(filters=None):
	columns, data = get_columns(), []
	condition = ""
	if filters.get("from_date") and filters.get("to_date"):
		condition += " and SI.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))
	query = ""
	if filters.get("sales_or_purchase") == "Sales":
		query = """ SELECT * FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)

	elif filters.get("sales_or_purchase") == "Purchase":
		query = """ SELECT * FROM `tabPurchase Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)

	si_or_pi = frappe.db.sql(query, as_dict=1)

	for i in si_or_pi:
		c_or_s = "Customer" if filters.get("sales_or_purchase") == "Sales" else "Supplier"
		i['party'] = i.customer if c_or_s == "Customer" else i.supploer

		i['vat_number'] = frappe.db.get_value("Customer", i['party'], "tax_id")
		i['total_amount'] = i.total - i.discount_amount

		data.append(i)

	if filters.get("summery"):
		query_total_si = """ SELECT SUM(SI.total) as total FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1 """

		query_total_pi = """ SELECT SUM(SI.total) as total FROM `tabPurchase Invoice` AS SI WHERE SI.docstatus = 1 """

		total_si = frappe.db.sql(query_total_si, as_dict=1)
		total_pi = frappe.db.sql(query_total_pi, as_dict=1)

		data.append({
			"name": "Sales Total",
			"total": total_si[0].total
		})
		data.append({
			"name": "Purchase Total",
			"total": total_pi[0].total
		})
	return columns, data
