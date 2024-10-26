# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AgentPaymentRequest(Document):
	@frappe.whitelist()
	def get_defaults(self):
		if self.company:
			defaults = {
			}
			tables = [
				"Agent Payment Request Defaults",
			]
			for table in tables:
				data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.company,
									 as_dict=1)
				if len(data) > 0:
					defaults[data[0].parentfield] = data[0]

			self.mode_of_payment = defaults['agent_payment_request_defaults'].mode_of_payment if 'agent_payment_request_defaults' in defaults else ""
			print("MODE OF PAAAYMENT")
			print(self.mode_of_payment)
	@frappe.whitelist()
	def get_sales_invoices(self):
		if self.agent_name:
			sales_invoices = frappe.db.sql(""" SELECT SI.name as sales_partner_payments,SI.sales_invoice_reference as sales_invoice, SI.posting_date, SI.status, SI.incentive, SI.invoice_net_amount as net_amount 
												FROM `tabSales Partner Payments` SI 
												WHERE SI.docstatus = 1 and SI.sales_partner_name = %s and SI.status='Unpaid' and company=%s""", (self.agent_name,self.company), as_dict=1)
			return sales_invoices
		return []
	def on_submit(self):
		if self.agent_outstanding_amount == 0 or self.claim_amount == 0:
			frappe.throw("Please Enter Claim Amount")
		for i in self.sales_invoice:
			frappe.db.sql(""" UPDATE `tabSales Invoice` SET agent_commision_record=1 WHERE name=%s""", i.sales_invoice)
			spp = frappe.get_doc("Sales Partner Payments", i.sales_partner_payments)
			status = ""
			pa = 0
			if float(spp.incentive) == float(i.incentive):
				pa = spp.incentive
				status = "Paid"
			elif float(i.incentive) > 0:
				pa = spp.paid_amount + i.incentive
				status = "Partly Paid"

			balance = spp.incentive - pa
			frappe.db.sql(
				""" UPDATE `tabSales Partner Payments` SET balance_amount=%s, paid_amount=%s, status=%s WHERE name=%s """,
				(balance, pa, status, i.sales_partner_payments)
			)
			frappe.db.commit()

		data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments Details` WHERE company=%s """, self.company, as_dict=1)
		if len(data) == 0:
			frappe.throw("Please check your Production Settings for Sales Partner Payments ")

		gl_debit = {
			"doctype": "GL Entry",
			"posting_date": self.posting_date,
			"account": data[0].payable_account,
			"debit": self.agent_outstanding_amount,
			"debit_in_account_currency": self.agent_outstanding_amount,
			"debit_in_transaction_currency": self.agent_outstanding_amount,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company,
			"transaction_exchange_rate": 1
		}

		credit_account = frappe.db.sql("""
			SELECT * FROM `tabMode of Payment Account` WHERE parent=%s AND company=%s LIMIT 1
		""", (self.mode_of_payment, self.company), as_dict=1)

		gl_credit = {
			"doctype": "GL Entry",
			"account": credit_account[0].default_account,
			"posting_date": self.posting_date,
			"credit": self.agent_outstanding_amount,
			"credit_in_account_currency": self.agent_outstanding_amount,
			"credit_in_transaction_currency": self.agent_outstanding_amount,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company,
			"transaction_exchange_rate": 1
		}

		debit = frappe.get_doc(gl_debit).insert(ignore_permissions=1)
		debit.submit()
		credit = frappe.get_doc(gl_credit).insert(ignore_permissions=1)
		credit.submit()

	def on_cancel(self):
		frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE docstatus=1 and voucher_no=%s and is_cancelled=0 """,self.name,as_dict=1)
		frappe.db.commit()
		for i in self.sales_invoice:
			frappe.db.sql(""" UPDATE `tabSales Invoice` SET agent_commision_record=0 WHERE name=%s""", i.sales_invoice)
			spp = frappe.get_doc("Sales Partner Payments", i.sales_partner_payments)
			status = ""
			balance = 0
			pa = spp.paid_amount - i.incentive
			if pa > 0:
				balance = spp.incentive - pa
				status = "Partly Paid"
			elif pa == 0:
				balance = spp.incentive
				status = "Unpaid"

			frappe.db.sql(
				""" UPDATE `tabSales Partner Payments` SET balance_amount=%s,paid_amount=%s, status=%s WHERE name=%s """,
				(balance, pa, status, i.sales_partner_payments))
			frappe.db.commit()

	def validate(self):
		if self.agent_outstanding_amount == 0 or self.claim_amount == 0:
			frappe.throw("Please Enter Claim Amount")
	# @frappe.whitelist()
	# def generate_journal_entry(self):
	# 	doc_jv = {
	# 		"doctype": "Journal Entry",
	# 		"voucher_type": "Journal Entry",
	# 		"posting_date": self.posting_date,
	# 		"accounts": self.jv_accounts(),
	# 		"agent_payment_request": self.name,
	# 	}
    #
	# 	jv = frappe.get_doc(doc_jv)
	# 	jv.insert(ignore_permissions=1)
	# 	# jv.submit()
	# 	return jv.name

	# @frappe.whitelist()
	# def jv_accounts(self):
		# accounts = []
		# data = frappe.db.sql(""" SELECT * FROM `tabSales Partner Payments Details` WHERE company=%s """,self.company, as_dict=1)
		# if len(data) == 0:
		# 	frappe.throw("Please check your Production Settings for Sales Partner Payments ")
		# accounts.append({
		# 	'account': data[0].payable_account,
		# 	'debit_in_account_currency': self.agent_outstanding_amount,
		# 	'credit_in_account_currency': 0,
		# })


		# if len(credit_acount) > 0:
		# 	accounts.append({
		# 		'account': credit_acount[0].default_account,
		# 		'debit_in_account_currency': 0,
		# 		'credit_in_account_currency': self.agent_outstanding_amount,
		# 		'party_type': "Employee",
		# 		'party': self.employee,
		# 	})
		# print(accounts)
		# return accounts

@frappe.whitelist()
def get_jv(name):
	jv = frappe.db.sql(""" SELECT * FROM `tabJournal Entry` WHERE agent_payment_request=%s and docstatus=1""",name, as_dict=1)
	if len(jv) > 0:
		return True
	return False