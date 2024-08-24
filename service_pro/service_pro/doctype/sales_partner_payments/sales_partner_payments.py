# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesPartnerPayments(Document):
	def on_submit(self):
		doc_jv = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.posting_date,
			"custom_sales_partner_payment": self.name,
			"accounts": self.jv_accounts_unpaid(),
		}
		print(doc_jv)
		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		jv.submit()

	def jv_accounts_unpaid(self):
		accounts = []
		accounts.append({
			'account': self.expense_account,
			'debit_in_account_currency': self.incentive,
			'credit_in_account_currency': 0,
			'cost_center': self.cost_center,
		})
		accounts.append({
			'account': self.payable_account,
			'debit_in_account_currency': 0,
			'credit_in_account_currency': self.incentive
		})
		return accounts