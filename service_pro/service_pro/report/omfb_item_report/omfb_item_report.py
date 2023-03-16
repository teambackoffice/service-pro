# Copyright (c) 2023, momscode and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	conditions=get_conditions(filters)
	condition=get_condition(filters)
	purchase_lists=get_purchase_lists(filters)
	for li in purchase_lists:
		row=frappe._dict({
				'item_code':li.item_code,
				'item_name':li.item_name,
				'date':li.date,
				'party_reference':li.party_reference,
				'invoice_reference':li.invoice_reference,
				'qty':li.qty,
				'rate':li.rate,
				'invoice_amount':li.invoice_amount,
				'status':li.status,

			})
		data.append(row)

	return columns,data

def get_columns():
	return[
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link","options":"Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "data","width": 150},
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date","width": 100},
		{"label": _("Party Reference"), "fieldname": "party_reference", "fieldtype": "Dynamic Link","width": 150},
		{"label": _("Invoice Reference"), "fieldname": "invoice_reference", "fieldtype": "Dynamic Link","width": 150},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency","width": 130},
		{"label": _("Invoice Amount"), "fieldname": "invoice_amount", "fieldtype": "Currency","width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data","width": 130},

	]
def get_purchase_lists(filters):

	conditions=get_conditions(filters)
	condition=get_condition(filters)
	data=[]

	purchase=frappe.db.sql("""SELECT
	p.item_code,
	p.item_name,
	p.qty,
	p.rate,
	p.amount as invoice_amount,
	p1.posting_date as date,
	p1.supplier as party_reference,
	p1.name as invoice_reference,
	p1.status
	FROM `tabPurchase Invoice Item` AS p  
	INNER JOIN `tabPurchase Invoice` AS p1 ON p1.name=p.parent
	INNER JOIN `tabItem` AS i ON p.item_code=i.item_code
	where i.is_omfb_item=1 and p1.docstatus=1
	{0}""".format(conditions),as_dict=1)
	if filters.get("customer"):
		purchase=""
	if filters.get("supplier"):
		print("************")
		sales=""
	else:
		sales=frappe.db.sql("""SELECT
		p.item_code,
		p.item_name,
		p.qty,
		p.rate,
		p.amount as invoice_amount,
		p1.posting_date as date,
		p1.customer as party_reference,
		p1.name as invoice_reference,
		p1.status
		FROM `tabSales Invoice Item` AS p  
		INNER JOIN `tabSales Invoice` AS p1 ON p1.name=p.parent
		INNER JOIN `tabItem` AS i ON p.item_code=i.item_code
		where i.is_omfb_item=1 and p1.docstatus=1
		{0}""".format(condition),as_dict=1)
	for dic_p in purchase:
		dic_p["indent"] = 0
		filters=conditions
		data.append(dic_p)


	
	for dic_p in sales:
		dic_p["indent"] = 0
		filters=conditions
		data.append(dic_p)
	
	return data

def get_conditions(filters):
	conditions=""
	if filters.get("posting_date"):
		conditions += " and p1.posting_date = '{0}' ".format(filters.get("posting_date"))
	if filters.get("supplier"):
		conditions += " and p1.supplier='{0}' ".format(filters.get("supplier"))
	if filters.get("item"):
		conditions += " and p.item_code='{0}'".format(filters.get("item"))
	return conditions

def get_condition(filters):
	condition=""
	if filters.get("posting_date"):
		condition += " and p1.posting_date = '{0}' ".format(filters.get("posting_date"))
	if filters.get("customer"):
		condition += " and p1.customer='{0}' ".format(filters.get("customer"))
	if filters.get("item"):
		condition += " and p.item_code='{0}'".format(filters.get("item"))
	return condition







