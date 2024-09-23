import frappe

# def on_so_submit(doc, method=None):
# 	if doc.selling_price_list:
# 		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
# 			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
# 			over_disc = frappe.db.exists("Sales Order Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
# 			if max_disc and over_disc:
# 				frappe.throw("Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Sales Order Item", over_disc, ['item_code'])))
	
# 	if doc.custom_production:
# 		for prod in doc.custom_production:
# 			if prod.reference:
# 				pd = frappe.get_doc("Production",prod.reference)
# 				if prod.qty <= pd.qty:
# 					frappe.db.set_value("Production", prod.reference, "status", "Partially Sales Order")
# 					frappe.db.commit()

# 				else:
# 					frappe.db.set_value("Production", prod.reference, "status", "Completed")
# 					frappe.db.commit()
@frappe.whitelist()
def sales_order_submit(doc, method):
	frappe.db.set_value('Service Order Form', doc.custom_service_order_form_id, 'status', 'Converted')
	
	frappe.db.commit()


from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_sales_order_from_service_order(source_name, target_doc=None):
    doclist = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Service Order Form",
                "field_map": {
                    "customer": "customer",
                   
                }
            }
        },
        target_doc,
    )

    return doclist
