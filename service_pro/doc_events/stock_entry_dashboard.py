from frappe import _


# Todo: non_standard_fieldnames is to be decided
def get_stock_entry_data(data):
	return {
		"fieldname": "stock_entry",
		"non_standard_fieldnames": {
			# "DocType Name": "Reference field name",
		},
		"internal_links": {
			"Purchase Order": ["items", "purchase_order"],
			"Inter Company Stock Transfer": ["items", "custom_inter_company_stock_transfer"],
			"Subcontracting Order": ["items", "subcontracting_order"],
			"Subcontracting Receipt": ["items", "subcontracting_receipt"],
			"Production": ["items", "custom_production_id"],
		},
		"transactions": [
			{
				"label": _("Reference"),
				"items": [
					"Purchase Order",
					"Subcontracting Order",
					"Subcontracting Receipt",
					"Inter Company Stock Transfer",
					"Production",
				],
			},
		],
	}
