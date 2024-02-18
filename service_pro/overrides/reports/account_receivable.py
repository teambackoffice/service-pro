import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import (
	ReceivablePayableReport,
)

# from frappe import _


def execute(filters=None):
	args = {
		"party_type": "Customer",
		"party": filters.get("customer"),
		"account_type": "Receivable",
		"naming_by": ["Selling Settings", "cust_master_name"],
	}
	return CustomReceivableReport(filters).run(args)


class CustomReceivableReport(ReceivablePayableReport):
	def append_row(self, row):
		super().append_row(row)
		self.set_notes(row)

	def set_notes(self, row):
		note = frappe.db.get_value("Sales Invoice", row.voucher_no, "notes")
		customers_po = frappe.db.get_value("Sales Invoice", row.voucher_no, "po_no")
		if note:
			row["notes"] = note
			row["po_no"] = customers_po

	def get_columns(self):
		super().get_columns()

		self.columns.append(
			dict(
				label="Remarks",
				fieldname="notes",
				fieldtype="data",
			)
		)
