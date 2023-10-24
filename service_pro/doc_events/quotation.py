import frappe

def on_cancel_quotation(doc, method):
    print("QUOTATION!!!!")
    frappe.db.sql(""" UPDATE `tabService Receipt Note` SET quotation="" WHERE name=%s  """, doc.service_receipt_note)
    frappe.db.commit()

def on_submit_quotation(doc, method=None):
	if doc.selling_price_list:
		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
			over_disc = frappe.db.exists("Quotation Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
			if max_disc and over_disc:
				frappe.throw("Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Quotation Item", over_disc, ['item_code'])))
                