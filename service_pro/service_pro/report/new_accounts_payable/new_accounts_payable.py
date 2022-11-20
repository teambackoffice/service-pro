# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

from service_pro.service_pro.report.new_accounts_receivable.new_accounts_receivable import ReceivablePayableReport


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return ReceivablePayableReport(filters).run(args)