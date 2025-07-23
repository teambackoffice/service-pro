# Copyright (c) 2025, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class InterCompanyJournalEntry(Document):
	def validate(self):
		self.validate_debit_credit_balance()
		self.validate_party()
	def on_submit(self):
		self.make_inter_company_journal_entry()

	def make_inter_company_journal_entry(self):
		company_groups = {}
		
		for row in self.details:
			if row.company not in company_groups:
				company_groups[row.company] = []
			company_groups[row.company].append(row)
		
		for company, rows in company_groups.items():
			entry = frappe.new_doc("Journal Entry")
			entry.posting_date = self.posting_date
			entry.company = company
			entry.custom_inter_company_journal_entry = self.name
		
			for row in rows:
				entry.append(
					"accounts",
					{
						"account": row.account,
						"party_type": row.party_type,
						"party": row.party,
						"debit_in_account_currency": row.debit,
						"credit_in_account_currency": row.credit
					},
				)
			
			entry.save()
	
	def validate_debit_credit_balance(self):
		company_totals = {}
		
		for row in self.details:
			if row.company not in company_totals:
				company_totals[row.company] = {'debit': 0, 'credit': 0}
			
			company_totals[row.company]['debit'] += row.debit or 0
			company_totals[row.company]['credit'] += row.credit or 0
		
		for company, totals in company_totals.items():
			debit_total = totals['debit']
			credit_total = totals['credit']
			
			if abs(debit_total - credit_total) > 0.01:  
				frappe.throw(
					f"For company '{company}': Total Debit ({debit_total}) does not equal Total Credit ({credit_total}). "
					f"Difference: {abs(debit_total - credit_total)}"
				)

	def validate_party(self):
		for d in self.get("details"):
			account_type = frappe.get_cached_value("Account", d.account, "account_type")
			if account_type in ["Receivable", "Payable"]:
				if not (d.party_type and d.party):
					frappe.throw(
						_(
							"Row {0}: Party Type and Party is required for Receivable / Payable account {1}"
						).format(d.idx, d.account)
					)
				elif (
					d.party_type
					and frappe.db.get_value("Party Type", d.party_type, "account_type") != account_type
				):
					frappe.throw(
						_("Row {0}: Account {1} and Party Type {2} have different account types").format(
							d.idx, d.account, d.party_type
						)
					)