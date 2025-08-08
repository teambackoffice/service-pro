# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def get_columns():
	return [
			{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "100"},
			{"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": "220"},
			{"label": "VAT Number", "fieldname": "vat_number", "fieldtype": "Data", "width": "120"},
			{"label": "Invoice Number", "fieldname": "name", "fieldtype": "Data", "width": "170"},
			{"label": "Amount", "fieldname": "total", "fieldtype": "Currency", "width": "130"},
			{"label": "Discount", "fieldname": "discount_amount", "fieldtype": "Currency","width": "100"},
			{"label": "VAT", "fieldname": "total_taxes_and_charges", "fieldtype": "Currency","width": "100"},
			{"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency","width": "100"},
			{"label": "Company", "fieldname": "company", "fieldtype": "	Link", "options": "Company","width": "250"},

		]

def execute(filters=None):
	columns, data = get_columns(), []
	condition = ""
	if filters.get("from_date") and filters.get("to_date"):
		condition += " and SI.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("company"):
		condition += " and SI.company = '{0}' ".format(filters.get("company"))

	if "Sales" in filters.get("sales_or_purchase"):
		query_si = """ SELECT * FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)

		si_or_pi = frappe.db.sql(query_si, as_dict=1)
		for i in si_or_pi:
			i['party'] = frappe.db.get_value("Customer", i.customer , "customer_name")
			i['vat_number'] = frappe.db.get_value("Customer",i.customer , "tax_id")
			i['total_amount'] = i.total - i.discount_amount
			data.append(i)

	if "Purchase" in filters.get("sales_or_purchase"):
		query_pi = """ SELECT * FROM `tabPurchase Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)
		si_or_pi = frappe.db.sql(query_pi, as_dict=1)
		for i in si_or_pi:
			i['party'] = frappe.db.get_value("Supplier", i.supplier, "supplier_name")
			i['vat_number'] = frappe.db.get_value("Supplier", i.supplier, "tax_id")
			i['total_amount'] = i.total - i.discount_amount
			data.append(i)

	if "Expense Claim" in filters.get("sales_or_purchase"):
		query_ec = """ SELECT * FROM `tabExpense Claim` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)
		expense_claims = frappe.db.sql(query_ec, as_dict=1)
		for i in expense_claims:
			i['party'] = frappe.db.get_value("Employee", i.employee, "employee_name")
			i['vat_number'] = "" 
			i['total'] = i.total_claimed_amount  
			i['discount_amount'] = 0  
			i['total_amount'] = i.grand_total  
			data.append(i)

	if "Sales" in filters.get("sales_or_purchase") and "Purchase" in filters.get("sales_or_purchase"):
		query_si = """ SELECT SUM(total) as total,SUM(discount_amount) as discount_amount,SUM(total_taxes_and_charges) as total_taxes_and_charges  FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)
		query_pi = """ SELECT SUM(total) as total,SUM(discount_amount) as discount_amount,SUM(total_taxes_and_charges) as total_taxes_and_charges  FROM `tabPurchase Invoice` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)

		si = frappe.db.sql(query_si, as_dict=1)
		pi = frappe.db.sql(query_pi, as_dict=1)

		data.append({
			"name": "Sales Total",
			"total": si[0].total,
			"discount_amount": si[0].discount_amount,
			"total_taxes_and_charges": si[0].total_taxes_and_charges,
			"total_amount": si[0].total - si[0].discount_amount,
		})
		data.append({
			"name": "Purchase Total",
			"total": pi[0].total,
			"discount_amount": pi[0].discount_amount,
			"total_taxes_and_charges": pi[0].total_taxes_and_charges,
			"total_amount": pi[0].total - pi[0].discount_amount,
		})
		data.append({
			"name": "Difference",
			"total": abs(si[0].total - pi[0].total),
			"discount_amount": abs(si[0].discount_amount - pi[0].discount_amount),
			"total_taxes_and_charges": abs(si[0].total_taxes_and_charges - pi[0].total_taxes_and_charges),
			"total_amount": abs((si[0].total - si[0].discount_amount) - (pi[0].total - pi[0].discount_amount)),
		})

	if "Expense Claim" in filters.get("sales_or_purchase") and (
		"Sales" in filters.get("sales_or_purchase") or "Purchase" in filters.get("sales_or_purchase")
	):
		query_ec = """ SELECT SUM(total_claimed_amount) as total,SUM(total_taxes_and_charges) as total_taxes_and_charges,SUM(grand_total) as grand_total  FROM `tabExpense Claim` AS SI WHERE SI.docstatus = 1  {0}""".format(condition)
		ec = frappe.db.sql(query_ec, as_dict=1)
		
		data.append({
			"name": "Expense Claim Total",
			"total": ec[0].total,
			"discount_amount": 0,
			"total_taxes_and_charges": ec[0].total_taxes_and_charges,
			"total_amount": ec[0].grand_total,
		})

	if filters.get("summery"):
		summery_condition = ""
		if filters.get("company"):
			summery_condition = " AND SI.company = '{0}' ".format(filters.get("company"))
			
		query_total_si = """ SELECT SUM(SI.total) as total FROM `tabSales Invoice` AS SI WHERE SI.docstatus = 1 {0}""".format(summery_condition)
		query_total_pi = """ SELECT SUM(SI.total) as total FROM `tabPurchase Invoice` AS SI WHERE SI.docstatus = 1 {0}""".format(summery_condition)
		query_total_ec = """ SELECT SUM(SI.grand_total) as total FROM `tabExpense Claim` AS SI WHERE SI.docstatus = 1 {0}""".format(summery_condition)

		total_si = frappe.db.sql(query_total_si, as_dict=1)
		total_pi = frappe.db.sql(query_total_pi, as_dict=1)
		total_ec = frappe.db.sql(query_total_ec, as_dict=1)

		data.append({
			"name": "Overall Sales Total",
			"total": total_si[0].total
		})
		data.append({
			"name": "Overall Purchase Total",
			"total": total_pi[0].total
		})
		data.append({
			"name": "Overall Expense Claim Total",
			"total": total_ec[0].total
		})
		data.append({
			"name": "Overall Difference",
			"total": abs(total_si[0].total - total_pi[0].total)
		})
	return columns, data
