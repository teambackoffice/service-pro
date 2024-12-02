from frappe import _


def purchase_order_dashboard(data):
	return {
		"fieldname": "purchase_order",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
			"Payment Entry": "reference_name",
			"Payment Request": "reference_name",
			"Auto Repeat": "reference_document",
		},
		"internal_links": {
			"Material Request": ["items", "material_request"],
			"Supplier Quotation": ["items", "supplier_quotation"],
			"Project": ["items", "project"],
			"Supplier Packing Slip": ["supplier_packing_slip_item", "po_ref"],
		},
		"transactions": [
			{"label": _("Related"), "items": ["Purchase Receipt", "Purchase Invoice", "Supplier Packing Slip"]},
			{"label": _("Payment"), "items": ["Payment Entry", "Journal Entry", "Payment Request"]},
			{
				"label": _("Reference"),
				"items": ["Material Request", "Supplier Quotation", "Project", "Auto Repeat"],
			},
			{
				"label": _("Sub-contracting"),
				"items": ["Subcontracting Order", "Subcontracting Receipt", "Stock Entry"],
			},
			{"label": _("Internal"), "items": ["Sales Order"]},
		],
	}


def purchase_receipt(data):
	return {
		"fieldname": "purchase_receipt_no",
		"non_standard_fieldnames": {
			"Purchase Invoice": "purchase_receipt",
			"Asset": "purchase_receipt",
			"Landed Cost Voucher": "receipt_document",
			"Auto Repeat": "reference_document",
			"Purchase Receipt": "return_against",
			"Stock Reservation Entry": "from_voucher_no",
		},
		"internal_links": {
			"Material Request": ["items", "material_request"],
			"Purchase Order": ["items", "purchase_order"],
			"Project": ["items", "project"],
			"Quality Inspection": ["items", "quality_inspection"],
			"Supplier Packing Slip": ["items", "custom_supplier_packing_slip"],
		},
		"transactions": [
			{
				"label": _("Related"),
				"items": ["Purchase Invoice", "Landed Cost Voucher", "Asset", "Stock Reservation Entry"],
			},
			{
				"label": _("Reference"),
				"items": ["Material Request", "Purchase Order", "Quality Inspection", "Project", "Supplier Packing Slip"],
			},
			{"label": _("Returns"), "items": ["Purchase Receipt"]},
			{"label": _("Subscription"), "items": ["Auto Repeat"]},
		],
	}


def sales_order_dashboard(data):
	return {
		"fieldname": "sales_order",
		"non_standard_fieldnames": {
			"Delivery Note": "against_sales_order",
			"Journal Entry": "reference_name",
			"Payment Entry": "reference_name",
			"Payment Request": "reference_name",
			"Auto Repeat": "reference_document",
			"Maintenance Visit": "prevdoc_docname",
			"Stock Reservation Entry": "voucher_no",
		},
		"internal_links": {
			"Quotation": ["items", "prevdoc_docname"],
		},
		"transactions": [
			{
				"label": _("Fulfillment"),
				"items": ["Sales Invoice", "Pick List", "Delivery Note", "Maintenance Visit"],
			},
			{"label": _("Purchasing"), "items": ["Material Request", "Purchase Order"]},
			{"label": _("Projects"), "items": ["Project"]},
			{"label": _("Manufacturing"), "items": ["Work Order"]},
			{"label": _("Reference"), "items": ["Quotation", "Auto Repeat", "Stock Reservation Entry"]},
			{"label": _("Payment"), "items": ["Payment Entry", "Payment Request", "Journal Entry"]},
			{"label": _("Production"), "items": ["Production"]},
		],
	}