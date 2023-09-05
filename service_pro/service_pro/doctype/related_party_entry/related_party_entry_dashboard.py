from frappe import _

def get_data():
	return {
		"fieldname": "related_party_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "related_party_entry"
		},
		"transactions": [
			{
				"label": _("Payment"),
				"items": [
					"Journal Entry"
				]
			}
        ]
	}