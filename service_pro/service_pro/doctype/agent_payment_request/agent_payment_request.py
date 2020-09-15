# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AgentPaymentRequest(Document):
	def generate_journal_entry(self):
		doc_jv = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.posting_date,
			"accounts": self.jv_accounts(),
			"agent_payment_request": self.name,
		}

		jv = frappe.get_doc(doc_jv)
		jv.insert(ignore_permissions=1)
		# jv.submit()
		return jv.name
	def jv_accounts(self):
		accounts = []
		amount = 0

		accounts.append({
			'account': self.liabilities_account,
			'debit_in_account_currency': self.agent_outstanding_amount,
			'credit_in_account_currency': 0,
		})

		credit_acount = frappe.db.sql(""" SELECT * FROM `tabMode of Payment Account` WHERE parent=%s LIMIT 1""", self.mode_of_payment,as_dict=1)

		if len(credit_acount) > 0:
			accounts.append({
				'account': credit_acount[0].default_account,
				'debit_in_account_currency': 0,
				'credit_in_account_currency': self.agent_outstanding_amount,
				'party_type': "Employee",
				'party': self.employee,
			})
		print(accounts)
		return accounts

@frappe.whitelist()
def get_jv(name):
	jv = frappe.db.sql(""" SELECT * FROM `tabJournal Entry` WHERE agent_payment_request=%s""",name, as_dict=1)
	if len(jv) > 0:
		return True
	return False