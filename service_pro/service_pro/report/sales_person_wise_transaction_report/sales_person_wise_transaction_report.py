# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _, msgprint, qb
from frappe.query_builder import Criterion
from frappe.utils import flt
from frappe.query_builder.functions import Avg
from erpnext import get_company_currency
from erpnext.stock.utils import get_incoming_rate


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	entries = get_entries(filters)
	item_details = get_item_details()
	data = []

	company_currency = get_company_currency(filters.get("company"))

	for d in entries:
		if d.total_qty > 0 or filters.get("show_return_entries", 0):
			# Calculate buying amount for this entry
			buying_amount = calculate_buying_amount(d, filters)
			
			# Calculate gross profit and gross profit percent
			gross_profit = flt(d.contribution_amt - buying_amount, 2)
			gross_profit_percent = 0.0
			if d.contribution_amt:
				gross_profit_percent = flt((gross_profit / d.contribution_amt) * 100.0, 2)
			
			data.append(
				[
					d.name,
					d.customer,
					d.territory,
					d.posting_date,
					d.net_total,
					buying_amount,  
					d.total_taxes_and_charges,
					d.grand_total,
					d.sales_person,
					d.contribution_amt,
					gross_profit,  # New gross profit column
					gross_profit_percent,  # New gross profit percent column
					company_currency,
				]
			)

	if data:
		total_row = [""] * len(data[0])
		data.append(total_row)

	return columns, data


def get_columns(filters):
	if not filters.get("doc_type"):
		msgprint(_("Please select the document type first"), raise_exception=1)

	columns = [
		{
			"label": _(filters["doc_type"]),
			"options": filters["doc_type"],
			"fieldname": frappe.scrub(filters["doc_type"]),
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Customer"),
			"options": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Territory"),
			"options": "Territory",
			"fieldname": "territory",
			"fieldtype": "Link",
			"width": 140,
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 140},
		{
			"label": _("Net Total"),
			"options": "currency",
			"fieldname": "net_total",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Buying Amount"),
			"options": "currency",
			"fieldname": "buying_amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Vat Amount"),
			"options": "currency",
			"fieldname": "total_taxes_and_charges",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Grand Total"),
			"options": "currency",
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Sales Person"),
			"options": "Sales Person",
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Contribution Amount"),
			"options": "currency",
			"fieldname": "contribution_amt",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Gross Profit"),  # New column
			"options": "currency",
			"fieldname": "gross_profit",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Gross Profit Percent"),  # New column
			"fieldname": "gross_profit_percent",
			"fieldtype": "Percent",
			"width": 140,
		},
		{
			"label": _("Currency"),
			"options": "Currency",
			"fieldname": "currency",
			"fieldtype": "Link",
			"hidden": 1,
		},
	]

	return columns


def calculate_buying_amount(entry, filters):
	"""
	Calculate buying amount for sales person contribution
	Similar to gross profit report logic but adapted for this report
	"""
	doc_type = filters["doc_type"]
	total_buying_amount = 0.0
	
	# Get all items for this document and sales person
	if doc_type == "Sales Invoice":
		items = frappe.db.sql("""
			SELECT 
				si_item.item_code,
				si_item.warehouse,
				si_item.stock_qty as qty,
				si_item.base_net_amount,
				si_item.name as item_row,
				si.update_stock,
				si_item.dn_detail,
				si_item.delivery_note,
				si_item.sales_order,
				si_item.so_detail,
				si_item.cost_center,
				si_item.project,
				si_item.serial_and_batch_bundle,
				si.posting_date,
				si.posting_time,
				'Sales Invoice' as parenttype,
				si.name as parent
			FROM 
				`tabSales Invoice` si,
				`tabSales Invoice Item` si_item,
				`tabSales Team` st
			WHERE 
				si.name = %s 
				AND si.name = si_item.parent
				AND st.parent = si.name
				AND st.sales_person = %s
				AND si.docstatus = 1
		""", (entry.name, entry.sales_person), as_dict=1)
		
	elif doc_type == "Sales Order":
		items = frappe.db.sql("""
			SELECT 
				so_item.item_code,
				so_item.warehouse,
				so_item.stock_qty as qty,
				so_item.base_net_amount,
				so_item.name as item_row,
				0 as update_stock,
				NULL as dn_detail,
				NULL as delivery_note,
				so.name as sales_order,
				so_item.name as so_detail,
				so_item.cost_center,
				so_item.project,
				NULL as serial_and_batch_bundle,
				so.transaction_date as posting_date,
				so.transaction_date as posting_time,
				'Sales Order' as parenttype,
				so.name as parent
			FROM 
				`tabSales Order` so,
				`tabSales Order Item` so_item,
				`tabSales Team` st
			WHERE 
				so.name = %s 
				AND so.name = so_item.parent
				AND st.parent = so.name
				AND st.sales_person = %s
				AND so.docstatus = 1
		""", (entry.name, entry.sales_person), as_dict=1)
	
	else:  # Delivery Note
		items = frappe.db.sql("""
			SELECT 
				dn_item.item_code,
				dn_item.warehouse,
				dn_item.stock_qty as qty,
				dn_item.base_net_amount,
				dn_item.name as item_row,
				1 as update_stock,
				dn_item.name as dn_detail,
				dn.name as delivery_note,
				dn_item.against_sales_order as sales_order,
				dn_item.so_detail,
				dn_item.cost_center,
				dn_item.project,
				dn_item.serial_and_batch_bundle,
				dn.posting_date,
				dn.posting_time,
				'Delivery Note' as parenttype,
				dn.name as parent
			FROM 
				`tabDelivery Note` dn,
				`tabDelivery Note Item` dn_item,
				`tabSales Team` st
			WHERE 
				dn.name = %s 
				AND dn.name = dn_item.parent
				AND st.parent = dn.name
				AND st.sales_person = %s
				AND dn.docstatus = 1
		""", (entry.name, entry.sales_person), as_dict=1)
	
	# Calculate buying amount for each item
	for item in items:
		item_buying_amount = get_item_buying_amount(item, filters)
		
		# Apply sales person allocation percentage
		allocation_percentage = entry.get('allocated_percentage', 100) or 100
		allocated_buying_amount = item_buying_amount * allocation_percentage / 100
		
		total_buying_amount += allocated_buying_amount
	
	return flt(total_buying_amount, 2)


def get_item_buying_amount(item, filters):
	"""
	Get buying amount for individual item using the exact same logic as gross profit report
	"""
	if not item.qty:
		return 0.0
	
	# Check if it's a non-stock item
	non_stock_items = get_non_stock_items()
	
	if item.item_code in non_stock_items and (item.project or item.cost_center):
		# For non-stock items, get last purchase rate
		buying_rate = get_last_purchase_rate(item.item_code, item, filters)
		return flt(item.qty) * flt(buying_rate)
	else:
		# For stock items, use the comprehensive buying amount logic
		return get_comprehensive_buying_amount(item, filters)


def get_comprehensive_buying_amount(item, filters):
	"""
	Comprehensive buying amount calculation using the same logic as gross profit report
	"""
	# Try to get from stock ledger entries first
	if (item.update_stock or item.dn_detail):
		buying_amount = get_buying_amount_from_sle(item, filters)
		if buying_amount:
			return buying_amount
	
	# Check if there are delivery notes for this item
	delivery_note_data = get_delivery_note_data(item, filters)
	if delivery_note_data:
		buying_amount = get_buying_amount_from_sle(delivery_note_data, filters)
		if buying_amount:
			return buying_amount
	
	# Check if from sales order
	if item.sales_order and item.so_detail:
		incoming_rate = get_buying_amount_from_so_dn(item.sales_order, item.so_detail, item.item_code)
		if incoming_rate:
			return flt(item.qty) * incoming_rate
	
	# Fallback to average buying rate
	buying_rate = get_average_buying_rate(item, filters)
	return flt(item.qty) * flt(buying_rate)


def get_buying_amount_from_sle(item, filters):
	"""
	Calculate buying amount from Stock Ledger Entries
	"""
	if not item.item_code or not item.warehouse:
		return 0.0
	
	# Get stock ledger entries for this item and warehouse
	sle = qb.DocType("Stock Ledger Entry")
	stock_entries = (
		qb.from_(sle)
		.select(
			sle.item_code,
			sle.voucher_type,
			sle.voucher_no,
			sle.voucher_detail_no,
			sle.stock_value,
			sle.warehouse,
			sle.actual_qty.as_("qty"),
		)
		.where(
			(sle.company == filters.get("company"))
			& (sle.item_code == item.item_code)
			& (sle.warehouse == item.warehouse)
			& (sle.is_cancelled == 0)
		)
		.orderby(sle.posting_datetime, sle.creation, order=qb.desc)
		.run(as_dict=True)
	)
	
	# Find the matching stock ledger entry
	parenttype = item.parenttype
	parent = item.parent
	if item.dn_detail:
		parenttype, parent = "Delivery Note", item.delivery_note
	
	for i, entry in enumerate(stock_entries):
		if (
			entry.voucher_type == parenttype
			and parent == entry.voucher_no
			and entry.voucher_detail_no == item.item_row
		):
			previous_stock_value = len(stock_entries) > i + 1 and flt(stock_entries[i + 1].stock_value) or 0.0
			
			if previous_stock_value:
				return abs(previous_stock_value - flt(entry.stock_value)) * flt(item.qty) / abs(flt(entry.qty))
			else:
				buying_rate = get_average_buying_rate(item, filters)
				return flt(item.qty) * buying_rate
	
	return 0.0


def get_delivery_note_data(item, filters):
	"""
	Get delivery note data for invoice items
	"""
	if filters["doc_type"] != "Sales Invoice" or not item.parent:
		return None
	
	dni = qb.DocType("Delivery Note Item")
	delivery_notes = (
		qb.from_(dni)
		.select(
			dni.against_sales_invoice.as_("sales_invoice"),
			dni.item_code,
			dni.warehouse,
			dni.parent.as_("delivery_note"),
			dni.name.as_("item_row"),
		)
		.where(
			(dni.docstatus == 1) 
			& (dni.against_sales_invoice == item.parent)
			& (dni.item_code == item.item_code)
		)
		.orderby(dni.creation, order=qb.desc)
		.limit(1)
		.run(as_dict=True)
	)
	
	if delivery_notes:
		dn_data = delivery_notes[0]
		return frappe._dict({
			"item_code": item.item_code,
			"warehouse": dn_data.warehouse,
			"qty": item.qty,
			"parenttype": "Delivery Note",
			"parent": dn_data.delivery_note,
			"item_row": dn_data.item_row
		})
	
	return None


def get_buying_amount_from_so_dn(sales_order, so_detail, item_code):
	"""
	Get average incoming rate from delivery notes linked to sales orders
	"""
	
	delivery_note_item = qb.DocType("Delivery Note Item")
	
	query = (
		qb.from_(delivery_note_item)
		.select(Avg(delivery_note_item.incoming_rate))
		.where(delivery_note_item.docstatus == 1)
		.where(delivery_note_item.item_code == item_code)
		.where(delivery_note_item.against_sales_order == sales_order)
		.where(delivery_note_item.so_detail == so_detail)
		.groupby(delivery_note_item.item_code)
	)
	
	result = query.run()
	return flt(result[0][0]) if result else 0


def get_average_buying_rate(item, filters):
	"""
	Get average buying rate using ERPNext's incoming rate function
	"""
	args = {
		"item_code": item.item_code,
		"warehouse": item.warehouse,
		"voucher_type": item.get("parenttype") or get_voucher_type(filters["doc_type"]),
		"voucher_no": item.get("parent"),
		"allow_zero_valuation": True,
		"company": filters.get("company"),
		"posting_date": item.get("posting_date"),
		"posting_time": item.get("posting_time")
	}
	
	if item.get("serial_and_batch_bundle"):
		args["serial_and_batch_bundle"] = item.serial_and_batch_bundle
	
	try:
		incoming_rate = get_incoming_rate(args)
		return flt(incoming_rate)
	except:
		# Fallback to standard valuation rate
		return get_standard_rate(item.item_code)


def get_last_purchase_rate(item_code, item, filters):
	"""
	Get last purchase rate for non-stock items
	"""
	purchase_invoice = qb.DocType("Purchase Invoice")
	purchase_invoice_item = qb.DocType("Purchase Invoice Item")
	
	query = (
		qb.from_(purchase_invoice_item)
		.inner_join(purchase_invoice)
		.on(purchase_invoice.name == purchase_invoice_item.parent)
		.select(
			purchase_invoice_item.base_rate / purchase_invoice_item.conversion_factor
		)
		.where(purchase_invoice.docstatus == 1)
		.where(purchase_invoice_item.item_code == item_code)
		.where(purchase_invoice.company == filters.get("company"))
	)
	
	if item.project:
		query = query.where(purchase_invoice_item.project == item.project)
	
	if item.cost_center:
		query = query.where(purchase_invoice_item.cost_center == item.cost_center)
	
	query = query.orderby(purchase_invoice.posting_date, order=qb.desc).limit(1)
	result = query.run()
	
	return flt(result[0][0]) if result else 0


def get_standard_rate(item_code):
	"""
	Fallback to get standard rate from item master
	"""
	return flt(frappe.db.get_value("Item", item_code, "standard_rate")) or 0


def get_voucher_type(doc_type):
	"""
	Map document type to voucher type
	"""
	mapping = {
		"Sales Invoice": "Sales Invoice",
		"Sales Order": "Sales Order", 
		"Delivery Note": "Delivery Note"
	}
	return mapping.get(doc_type, doc_type)


def get_non_stock_items():
	"""
	Get list of non-stock items
	"""
	return frappe.db.sql_list("""SELECT name FROM tabItem WHERE is_stock_item=0""")


def get_entries(filters):
	date_field = filters["doc_type"] == "Sales Order" and "transaction_date" or "posting_date"
	if filters["doc_type"] == "Sales Order":
		qty_field = "delivered_qty"
	else:
		qty_field = "qty"
	conditions, values = get_conditions(filters, date_field)

	entries = frappe.db.sql(
		"""
		SELECT
			dt.name, dt.customer, dt.territory, dt.{} as posting_date,
			dt.net_total, dt.total_taxes_and_charges, dt.grand_total,
			st.sales_person, st.allocated_percentage,
			SUM(CASE
				WHEN dt.status = "Closed" THEN dt_item.{} * dt_item.conversion_factor
				ELSE dt_item.stock_qty
			END) as total_qty,
			SUM(CASE
				WHEN dt.status = "Closed" THEN (dt_item.base_net_rate * dt_item.{} * dt_item.conversion_factor) * st.allocated_percentage/100
				ELSE dt_item.base_net_amount * st.allocated_percentage/100
			END) as contribution_amt
		FROM
			`tab{}` dt, `tab{} Item` dt_item, `tabSales Team` st
		WHERE
			st.parent = dt.name and dt.name = dt_item.parent and st.parenttype = {}
			and dt.docstatus = 1 {}
		GROUP BY
			dt.name, st.sales_person
		ORDER BY
			st.sales_person, dt.name desc
		""".format(
			date_field,
			qty_field,
			qty_field,
			filters["doc_type"],
			filters["doc_type"],
			"%s",
			conditions,
		),
		tuple([filters["doc_type"], *values]),
		as_dict=1,
	)

	return entries


def get_conditions(filters, date_field):
	conditions = [""]
	values = []

	for field in ["company", "customer", "territory"]:
		if filters.get(field):
			conditions.append(f"dt.{field}=%s")
			values.append(filters[field])

	if filters.get("sales_person"):
		lft, rgt = frappe.get_value("Sales Person", filters.get("sales_person"), ["lft", "rgt"])
		conditions.append(
			f"exists(select name from `tabSales Person` where lft >= {lft} and rgt <= {rgt} and name=st.sales_person)"
		)

	if filters.get("from_date"):
		conditions.append(f"dt.{date_field}>=%s")
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append(f"dt.{date_field}<=%s")
		values.append(filters["to_date"])

	items = get_items(filters)
	if items:
		conditions.append("dt_item.item_code in (%s)" % ", ".join(["%s"] * len(items)))
		values += items
	else:
		# return empty result, if no items are fetched after filtering on 'item group' and 'brand'
		conditions.append("dt_item.item_code = Null")

	return " and ".join(conditions), values


def get_items(filters):
	item = qb.DocType("Item")

	item_query_conditions = []
	if filters.get("item_group"):
		# Handle 'Parent' nodes as well.
		item_group = qb.DocType("Item Group")
		lft, rgt = frappe.db.get_all(
			"Item Group", filters={"name": filters.get("item_group")}, fields=["lft", "rgt"], as_list=True
		)[0]
		item_group_query = (
			qb.from_(item_group)
			.select(item_group.name)
			.where((item_group.lft >= lft) & (item_group.rgt <= rgt))
		)
		item_query_conditions.append(item.item_group.isin(item_group_query))
	if filters.get("brand"):
		item_query_conditions.append(item.brand == filters.get("brand"))

	items = qb.from_(item).select(item.name).where(Criterion.all(item_query_conditions)).run()
	return items


def get_item_details():
	item_details = {}
	for d in frappe.db.sql("""SELECT `name`, `item_group`, `brand` FROM `tabItem`""", as_dict=1):
		item_details.setdefault(d.name, d)

	return item_details