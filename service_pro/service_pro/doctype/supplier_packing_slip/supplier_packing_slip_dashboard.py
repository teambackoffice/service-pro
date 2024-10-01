from frappe import _


def get_data():
	return {
		"fieldname": "custom_supplier_packing_slip",
		"internal_links": {
			"Purchase Order": ["supplier_packing_slip_item", "po_ref"],
			
        },
		"transactions": [
            {"label": _("Related"), "items": ["Purchase Receipt"]},
			{"label": _("Reference"), "items": ["Purchase Order"]},			
		],
    }