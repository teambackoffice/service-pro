# Copyright (c) 2023, Wahni IT Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.contacts.doctype.address.address import get_default_address


@frappe.whitelist()
def get_party_details(party, party_type, args=None):
	out = {}
	billing_address = None

	billing_address_name = get_default_address(party_type, party)
	if not billing_address_name:
		address = frappe.db.get_all(
			"Dynamic Link",
			filters={
				"parenttype": "Address",
				"link_doctype": "Customer",
				"link_name": party,
			},
			pluck="parent",
		)

		billing_address_name = frappe.db.get_value(
			"Address",
			{
				"address_type": "Billing",
				"name": ["in", address],
			},
			"name",
		)

	if billing_address_name:
		billing_address = frappe.get_doc("Address", billing_address_name)

	if billing_address:
		out["billing_address_line1"] = billing_address.address_line1
		out["billing_address_line2"] = billing_address.address_line2
		out["billing_city"] = billing_address.city
		out["billing_county"] = billing_address.county
		out["billing_state"] = billing_address.state
		out["billing_zipcode"] = billing_address.pincode
		out["billing_country"] = billing_address.country

	return out
