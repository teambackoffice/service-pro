# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words


class ServiceOrderForm(Document):
	
	def validate(self):
		
		self.in_words = money_in_words(self.grand_total, self.currency)
