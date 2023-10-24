import frappe

def on_so_submit(doc, method=None):
	if doc.selling_price_list:
		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
			over_disc = frappe.db.exists("Sales Order Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
			if max_disc and over_disc:
				frappe.throw("Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Sales Order Item", over_disc, ['item_code'])))
	