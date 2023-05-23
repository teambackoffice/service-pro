# Copyright (c) 2022, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	conditions=get_conditions(filters)
	p_conditions = get_p_conditions(filters)
	date_conditions = get_date_conditions(filters)
	lists=get_lists(filters)
	for li in lists:
		row=frappe._dict({
				'posting_date':li.posting_date,
				'voucher_type':li.voucher_type,
				'reference':li.reference,
				'item_code':li.item_code,
				'item_name':li.item_name,
				'avail_qty':li.avail_qty,
				'purchase_qty':li.purchase_qty,
				'purchase_rate':li.purchase_rate,
				'lc_rate':li.lc_rate,
				'selling_rate':li.selling_rate,
			})	
		data.append(row)
	return columns,data

def get_columns():
	return[
		{
			"label": _("Date"), 
			"fieldname": "posting_date",
			"fieldtype":"Date", 
			"width": 120
		},
		
		{
			"label": _("Voucher Type"), 
			"fieldname": "voucher_type", 
			"width": 120
		},
		{
			"label": _("Reference"),
			"fieldname": "reference",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 150,
		},
		
		{
   			"fieldname": "item_code",
   			"fieldtype": "Link",
   			"label": "Item Code",
			"options":"Item",
			"width":210
			
 		},
		{
   			"fieldname": "item_name",
   			"fieldtype": "Data",
   			"label": "Item Name",
			"width":180,
			"hidden":1
			
 		},
		
		{
   			"fieldname": "avail_qty",
   			"fieldtype": "Float",
   			"label": "Avail Qty",
			"width":80
  		},
		
  		{
   			"fieldname": "purchase_qty",
   			"fieldtype": "Float",
   			"label": "Purchase Qty",
			"width":80 
  		},
		{
   			"fieldname": "purchase_rate",
   			"fieldtype": "Currency",
   			"label": "Purchase Rate",
			"width":120 
  		},
		{
   			"fieldname": "lc_rate",
   			"fieldtype": "Currency",
   			"label": "LC Rate",
			"width":120 
  		},	
		{
   			"fieldname": "selling_rate",
   			"fieldtype": "Currency",
   			"label": "Selling Rate",
			"width":140 
  		},
	]
def get_lists(filters):
	conditions=get_conditions(filters)
	p_conditions = get_p_conditions(filters)
	date_conditions = get_date_conditions(filters)
	data=[]
	if filters.get("item_code") or filters.get("from_date") and filters.get("to_date") or filters.get("item_group") or filters.get("price_list") or filters.get("supplier"):
		parent=frappe.db.sql("""SELECT
		p.name as reference,
		p.posting_date,
		pi.item_code,
		pi.item_name,
		pi.qty as purchase_qty,
		pi.rate as purchase_rate
		from `tabPurchase Invoice` as p
		inner join `tabPurchase Invoice Item` as pi 
		on p.name=pi.parent 
		inner join `tabItem` as i on i.name=pi.item_code where p.docstatus=1 {0}""".format(conditions),as_dict=1)
		if filters.get("price_list"):
			for dic_p in parent:
				dic_p["indent"] = 0
				price = frappe.db.sql("""select price_list_rate from `tabItem Price` where item_code =%s and {0} """.format(p_conditions),dic_p.item_code,as_dict=1)
				print("HOOOOOOOOOOOOOOOOOOOOOOOOOOO")
				print(price)
				if price:
					if price[0].price_list_rate:
						print("price list rate")
						print(price[0].price_list_rate)
						sr = {"selling_rate":price[0].price_list_rate}
						dic_p.update(sr)
					else:
						sr = {"selling_rate":0}
						dic_p.update(sr)
				else:
					sr = {"selling_rate":0}
					dic_p.update(sr)
				sf=frappe.db.sql("""select qty_after_transaction,incoming_rate from `tabStock Ledger Entry` where item_code=%s and is_cancelled=0 and {0} ORDER BY posting_date desc,posting_time desc limit 1""".format(date_conditions),dic_p.item_code,as_dict=1)
				print(sf)
				print("ssssssssssssssssssssssfffffffffffffffffffffff")
				if sf:
					if sf[0].qty_after_transaction:
						q = {'avail_qty':sf[0].qty_after_transaction}
						dic_p.update(q)
					else:
						q = {'avail_qty':0.00}
						dic_p.update(q)
					if sf[0].incoming_rate:
						i = {'lc_rate':sf[0].incoming_rate}
						dic_p.update(i)
					else:
						i = {'lc_rate':0.00}
						dic_p.update(i)
				else:
					q = {'avail_qty':0.00}
					dic_p.update(q)
					i = {'lc_rate':0.00}
					dic_p.update(i)

				name = {'voucher_type':'Purchase Invoice'}
				dic_p.update(name)
				filters=conditions
				filters+=p_conditions
				data.append(dic_p)
				
			return data
		else:
			for dic_p in parent:
				dic_p["indent"] = 0
				sf=frappe.db.sql("""select qty_after_transaction,incoming_rate from `tabStock Ledger Entry` where item_code=%s and is_cancelled=0 and {0} ORDER BY posting_date desc,posting_time desc limit 1""".format(date_conditions),dic_p.item_code,as_dict=1)
				print(sf)
				print("ssssssssssssssssssssssfffffffffffffffffffffff")
				if sf:
					if sf[0].qty_after_transaction:
						q = {'avail_qty':sf[0].qty_after_transaction}
						dic_p.update(q)
					else:
						q = {'avail_qty':0.00}
						dic_p.update(q)

					if sf[0].incoming_rate:
						i = {'lc_rate':sf[0].incoming_rate}
						dic_p.update(i)
					else:
						i = {'lc_rate':0.00}
						dic_p.update(i)
				else:
					q = {'avail_qty':0.00}
					dic_p.update(q)
					i = {'lc_rate':0.00}
					dic_p.update(i)

				name = {'voucher_type':'Purchase Invoice'}
				dic_p.update(name)
				filters=conditions
				filters+=p_conditions
				data.append(dic_p)
				
			return data
	else:
		parent=frappe.db.sql("""SELECT
		p.name as reference,
		p.posting_date,
		pi.item_code,
		pi.item_name,
		pi.qty as purchase_qty,
		pi.rate as purchase_rate
		from `tabPurchase Invoice` as p
		inner join `tabPurchase Invoice Item` as pi 
		on p.name=pi.parent 
		inner join `tabItem` as i on i.name=pi.item_code where p.docstatus=1""",as_dict=1)
		print("ayeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
		print(parent)
		for dic_p in parent:
			dic_p["indent"] = 0
			sf=frappe.db.sql("""select qty_after_transaction,incoming_rate from `tabStock Ledger Entry` where item_code=%s 
			and is_cancelled=0 ORDER BY posting_date desc,posting_time desc limit 1""",dic_p.item_code,as_dict=1)
			print(sf)
			print("ssssssssssssssssssssssfffffffffffffffffffffff")
			if sf:
				if sf[0].qty_after_transaction:
					q = {'avail_qty':sf[0].qty_after_transaction}
					dic_p.update(q)
				else:
					q = {'avail_qty':0.00}
					dic_p.update(q)

				if sf[0].incoming_rate:
					i = {'lc_rate':sf[0].incoming_rate}
					dic_p.update(i)
				else:
					i = {'lc_rate':0.00}
					dic_p.update(i)
			else:
				q = {'avail_qty':0.00}
				dic_p.update(q)
				i = {'lc_rate':0.00}
				dic_p.update(i)

				

			name = {'voucher_type':'Purchase Invoice'}
			dic_p.update(name)
			filters=conditions
			data.append(dic_p)
		return data

def get_conditions(filters):
	conditions=""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += "and p.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))
	if filters.get("supplier"):
		conditions += "and p.supplier ='{0}' ".format(filters.get("supplier"))
	if filters.get("item_code"):
		conditions += "and pi.item_code='{0}' ".format(filters.get("item_code"))
	if filters.get("item_group"):
		conditions += "and i.item_group='{0}' ".format(filters.get("item_group"))
	
	return conditions

def get_p_conditions(filters):
	p_conditions =""
	if filters.get("price_list"):
		p_conditions = "price_list='{0}' ".format(filters.get("price_list"))
	return p_conditions

def get_date_conditions(filters):
	date_conditions =""
	if filters.get("from_date") and filters.get("to_date"):
		date_conditions += "posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))
	return date_conditions