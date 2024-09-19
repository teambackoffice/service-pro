# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words


class ServiceOrderForm(Document):
	pass

	# def before_save(doc, method):
	# 	# Ensure that grand_total has a value before converting it to words
	# 	if doc.grand_total:
	# 		# Fetch the Company document to get the default currency
	# 		company = frappe.get_doc("Service Order Form", doc.service_order_form)

	# 		# Convert grand_total to words using the company's default currency
	# 		in_words = money_in_words(doc.grand_total, company.default_currency)

	# 		# Set the value of the in_words field
	# 		doc.in_words = in_words


from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum

@frappe.whitelist()
def create_sales_order(source_name, target_doc=None):
    def update_sales_team(source, target):
        if source.sales_executive:
            if not target.sales_team:
                target.append('sales_team', {
                    'sales_person': source.sales_executive,                     
                })

    doclist = get_mapped_doc(
        "Service Order Form",
        source_name,
        {
            "Service Order Form": {
                "doctype": "Sales Order",
                "field_map": {
                    "name": "custom_service_order_form_id", 
                    "customer": "customer"  
                }
            }
        },
        target_doc,
        update_sales_team  
    )

    return doclist





