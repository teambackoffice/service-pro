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

