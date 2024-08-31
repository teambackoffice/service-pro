# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesPartnerPayments(Document):
	def on_submit(self):
		gl_debit = {
			"doctype": "GL Entry",
			"posting_date": self.posting_date,
			"account": self.expense_account,
			"cost_center": self.cost_center,
			"credit": self.incentive,
			"credit_in_account_currency": self.incentive,
			"credit_in_transaction_currency": self.incentive,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company,
			"transaction_exchange_rate": 1
		}
		gl_credit = {
			"doctype": "GL Entry",
			"account": self.expense_account,
			"posting_date": self.posting_date,
			"cost_center": self.cost_center,
			"debit": self.incentive,
			"debit_in_account_currency": self.incentive,
			"debit_in_transaction_currency": self.incentive,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company,
			"transaction_exchange_rate": 1
		}
		debit = frappe.get_doc(gl_debit).insert(ignore_permissions=1)
		debit.submit()
		credit = frappe.get_doc(gl_credit).insert(ignore_permissions=1)
		credit.submit()

		# doc_jv = {
		# 	"doctype": "Journal Entry",
		# 	"voucher_type": "Journal Entry",
		# 	"posting_date": self.posting_date,
		# 	"custom_sales_partner_payment": self.name,
		# 	"accounts": self.jv_accounts_unpaid(),
		# }
		# print(doc_jv)
		# jv = frappe.get_doc(doc_jv)
		# jv.insert(ignore_permissions=1)
		# jv.submit()

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