# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
def get_columns():
	return [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "120"},
		{"label": "Document Name", "fieldname": "name", "fieldtype": "Data","width": "300"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer", "width": "200"},
		{"label": "Supplier Name", "fieldname": "supplier_name", "fieldtype": "Link", "options": "Supplier", "width": "200"},
		{"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Link", "options": "Mode of Payment", "width": "200"},
		{"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": "120"},
	]

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("party_type"):
		conditions += "and party_type='{0}' ".format(filters.get("party_type"))

	if filters.get("mode_of_payment"):
		conditions += "and mode_of_payment='{0}' ".format(filters.get("mode_of_payment"))

	return conditions

def execute(filters=None):
	columns, data = get_columns(), []
	conditions = get_conditions(filters)

	data = frappe.db.sql(""" SELECT * FROM `tabPayment Entry` WHERE docstatus=1 {0}""".format(conditions),as_dict=1)
	for i in data:
		i.supplier_name = i.party_name if i.party_type == 'Supplier' else ""
		i.customer_name = i.party_name if i.party_type == 'Customer' else ""
	return columns, data
