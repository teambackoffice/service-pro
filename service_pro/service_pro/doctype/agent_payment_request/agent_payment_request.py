# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AgentPaymentRequest(Document):
	@frappe.whitelist()
	def get_sales_invoices(self):
		if self.agent_name:
			sales_invoices = frappe.db.sql(""" SELECT SI.name as sales_partner_payments,SI.sales_invoice_reference as sales_invoice, SI.posting_date, SI.status, SI.incentive, SI.invoice_net_amount as net_amount 
												FROM `tabSales Partner Payments` SI 
												WHERE SI.docstatus = 1 and SI.sales_partner_name = %s """, self.agent_name, as_dict=1)
			return sales_invoices
		return []
	def on_submit(self):
		for i in self.sales_invoice:
			frappe.db.sql(""" UPDATE `tabSales Invoice` SET agent_commision_record=1 WHERE name=%s""", i.sales_invoice)
			frappe.db.commit()
	def on_cancel(self):
		for i in self.sales_invoice:
			frappe.db.sql(""" UPDATE `tabSales Invoice` SET agent_commision_record=0 WHERE name=%s""", i.sales_invoice)
			frappe.db.commit()

	# def validate(self):
	# 	if not self.liabilities_account:
	# 		frappe.throw("Please select liablities account for Sales Person " + self.agent_name)

	@frappe.whitelist()
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

	@frappe.whitelist()
	def jv_accounts(self):
		accounts = []
		data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments Details` WHERE company=%s """,self.company, as_dict=1)
		if len(data) == 0:
			frappe.throw("Please check your Production Settings for Sales Partner Payments ")
		accounts.append({
			'account': data[0].payable_account,
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
	jv = frappe.db.sql(""" SELECT * FROM `tabJournal Entry` WHERE agent_payment_request=%s and docstatus=1""",name, as_dict=1)
	if len(jv) > 0:
		return True
	return False