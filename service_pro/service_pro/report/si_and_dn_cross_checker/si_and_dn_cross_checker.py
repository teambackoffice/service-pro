# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
def get_columns():
	return [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "120"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data","width": "300"},
		{"label": "Sales Invoice", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": "200"},
		{"label": "Delivery Note", "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": "200"},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": "250"},
		{"label": "Update Stock", "fieldname": "update_stock", "fieldtype": "Data", "width": "120"},
		{"label": "Invoiced Qty", "fieldname": "invoiced_qty", "fieldtype": "Float", "width": "120"},
		{"label": "Delivery Qty", "fieldname": "delivery_qty", "fieldtype": "Float", "width": "110"},
		{"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": "110"},
		{"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": "110"},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": "110"},
	]
def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and SI.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("sales_invoice"):
		conditions += "and SI.name='{0}' ".format(filters.get("sales_invoice"))

	return conditions

def execute(filters=None):
	columns, data =get_columns(), []
	# limit_condition = " LIMIT 30" if (not filters.get("from_date") or not filters.get("from_date")) and not filters.get("from_date") else ""
	conditions = get_conditions(filters)
	data = frappe.db.sql(""" SELECT 
	 							SI.posting_date,
	 							SI.customer_name,
	 							SI.name as sales_invoice,
								SI.update_stock,
	 							SII.item_code,
	 							SII.item_name,
	 							SII.rate,
	 							SII.name as si_detail,
	 							SII.amount,
	 							SII.qty as invoiced_qty,
	 							SII.delivery_note
	 						FROM `tabSales Invoice` SI 
 							INNER JOIN `tabSales Invoice Item` SII ON SII.parent = SI.name
 							WHERE SI.docstatus = 1 {0}
 							""".format(conditions), as_dict=1)
	for i in data:
		if not i.delivery_note:
			dn = frappe.db.sql(""" SELECT * FROM `tabDelivery Note Item` WHERE si_detail=%s and against_sales_invoice=%s """, (i.si_detail, i.sales_invoice),as_dict=1)
			i.balance_qty = 0
			if len(dn) > 0:
				i.delivery_note = dn[0].parent
				i.delivery_qty = dn[0].qty
				i.balance_qty = i.invoiced_qty - i.delivery_qty
		else:
			dn = frappe.db.sql(
				""" SELECT * FROM `tabDelivery Note Item` WHERE parent=%s and item_code=%s """,
				(i.delivery_note, i.item_code), as_dict=1)
			i.balance_qty = 0
			if len(dn) > 0:
				i.delivery_qty = dn[0].qty
				i.balance_qty = i.invoiced_qty - i.delivery_qty
	return columns, data
