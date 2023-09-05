# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RelatedPartyEntry(Document):
	def before_submit(self):
		self.status = "Unpaid"

	@frappe.whitelist()
	def create_journal_entry(self, return_date=None, returned_from=None, return_amount=0):
		doc = frappe.new_doc("Journal Entry")
		doc.company = self.company
		doc.posting_date = self.posting_date
		doc.cheque_no = "Against Related Party Entry: {0}".format(self.name)
		doc.cheque_date = self.posting_date
		doc.user_remark = self.remarks
		doc.related_party_entry = self.name
		if self.type == "Credit To":
			doc.set("accounts", 
			[
				{
					"account":self.related_party_account,
					"debit_in_account_currency": self.amount,
					"credit_in_account_currency":0
				},
				{
					"account":self.account_for_payments,
					"debit_in_account_currency":0,
					"credit_in_account_currency": self.amount
				}
			])
		elif self.type == "Debit To":
			doc.set("accounts", 
			[
				{
					"account":self.account_for_payments,
					"debit_in_account_currency": self.amount,
					"credit_in_account_currency":0
				},
				{
					"account":self.related_party_account,
					"debit_in_account_currency":0,
					"credit_in_account_currency": self.amount
				}
			])
		doc.save(ignore_permissions=True)
		doc.submit()

		if doc.docstatus == 1:
			self.status = "Paid"
			self.save(ignore_permissions=True)
			
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def accounts_query(doctype, txt, searchfield, start, page_len, filters):
	query_filter = ""
	query_filter += "is_group = False AND"
	if filters.get("field") == "Related Party Account":
		query_filter += " root_type IN ('Asset', 'Liability')"
	if filters.get("field") == "Account For Payments" or filters.get("field") == "Returned From":
		query_filter += " root_type = 'Asset' AND"
	if filters.get("account_type"):
		query_filter += " account_type IN ('Bank', 'Cash')"
	if txt:
		txt = "AND name LIKE '%{0}%'".format(txt)
	acount_query = frappe.db.sql("""
		SELECT 
			name
		FROM
			`tabAccount`
		WHERE
			freeze_account = 'No' AND
			{query_filter}
			{txt}
		""".format(txt=txt, query_filter=query_filter))
	return acount_query

@frappe.whitelist()
def create_return_entry(related_party_entry=None, return_date=None, returned_from=None, return_amount=None):
	if not related_party_entry:
		return False
	return_amount = float(return_amount)
	doc = frappe.get_doc("Related Party Entry", related_party_entry)
	
	if return_amount == 0.0 or return_amount < 0.0:
		frappe.throw("Return amount should be greater than zero")
		return False
	elif return_amount > doc.amount:
		frappe.throw("Return amount should be less than paid amount")
	
	if doc.status == "Paid" or "Partially Returned":
		je = frappe.new_doc("Journal Entry")
		je.company = doc.company
		je.posting_date = return_date
		je.cheque_no = "Against Related Party Entry: {0}".format(doc.name)
		je.cheque_date = doc.posting_date
		je.user_remark = doc.remarks
		je.related_party_entry = doc.name
		je.is_related_party_entry_return = True
		if doc.type == "Credit To":
			je.set("accounts", 
			[
				{
					"account":returned_from,
					"debit_in_account_currency": return_amount,
					"credit_in_account_currency":0
				},
				{
					"account":doc.related_party_account,
					"debit_in_account_currency":0,
					"credit_in_account_currency": return_amount
				}
			])
		elif doc.type == "Debit To":
			je.set("accounts", 
			[
				{
					"account":returned_from,
					"debit_in_account_currency": return_amount,
					"credit_in_account_currency":0
				},
				{
					"account":doc.related_party_account,
					"debit_in_account_currency":0,
					"credit_in_account_currency": return_amount
				}
			])
		je.save(ignore_permissions=True)
		je.submit()

	if je.docstatus == 1:
		doc.return_date = return_date
		doc.returned_amount = doc.returned_amount + return_amount
		doc.pending_amount = doc.amount - doc.returned_amount
		doc.returned_from = returned_from
		if doc.pending_amount > 0.0:
			doc.status = "Partially Returned"
		elif doc.returned_amount == doc.amount:
			doc.status = "Returned"
		doc.save(ignore_permissions=True)