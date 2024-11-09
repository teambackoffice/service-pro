# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words


from frappe.model.document import Document
from frappe.utils import money_in_words
import frappe

class SalaryCertificate(Document):
    def validate(self):
        if self.amount:
            self.amount_in_words = money_in_words(self.amount)

@frappe.whitelist()
def get_amount_in_words(amount):
    amount_in_words = money_in_words(amount)
    return amount_in_words


