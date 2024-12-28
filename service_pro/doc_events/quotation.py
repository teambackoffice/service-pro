import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate


def on_cancel_quotation(doc, method):
    print("QUOTATION!!!!")
    frappe.db.sql(""" UPDATE `tabService Receipt Note` SET quotation="" WHERE name=%s  """, doc.service_receipt_note)
    frappe.db.commit()

def on_submit_quotation(doc, method=None):
	if doc.selling_price_list:
		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
			over_disc = frappe.db.exists("Quotation Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
			if max_disc and over_disc:
				frappe.throw("Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Quotation Item", over_disc, ['item_code'])))

def validate_item(self, method):
    if self.docstatus == 0:  
        for item in self.items:
            existing_quotations = frappe.get_all(
                "Quotation",
                filters={
                    "docstatus": 1, 
                    "name": ["!=", self.name], 
                },
                pluck="name"
            )

            if existing_quotations:
                item_details = frappe.get_all(
                    "Quotation Item",
                    filters={
                        "parent": ["in", existing_quotations],
                        "item_code": item.item_code,
                    },
                    fields=["parent"],
                    order_by="modified desc"  
                )

                item_count = len(item_details)

                if item_count > 0:
                    latest_quotations = [
                        frappe.get_value("Quotation", detail.get("parent"), ["name", "transaction_date"])
                        for detail in item_details[:5]
                    ]

                    quotation_details = "\n".join(
                        f"{quotation[0]} (Date: {quotation[1]})" for quotation in latest_quotations
                    )

                    if item_count == 1:
                        frappe.msgprint(
                            _("The item {0} has already been quoted in Quotation:\n{1}").format(
                                item.item_code, quotation_details
                            )
                        )
                    elif item_count == 2:
                        frappe.msgprint(
                            _("The item {0} has already been quoted in Quotations:\n{1}").format(
                                item.item_code, quotation_details
                            )
                        )
                    elif item_count >= 3:
                        frappe.msgprint(
                            _("The item {0} has already been quoted {1} times in the following Quotations:\n{2}").format(
                                item.item_code, item_count, quotation_details
                            )
                        )


         

@frappe.whitelist()
def make_sales_order_so(source_name: str, target_doc=None):
	if not frappe.db.get_singles_value(
		"Selling Settings", "allow_sales_order_creation_for_expired_quotation"
	):
		quotation = frappe.db.get_value(
			"Quotation", source_name, ["transaction_date", "valid_till"], as_dict=1
		)
		if quotation.valid_till and (
			quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())
		):
			frappe.throw(_("Validity period of this quotation has ended."))

	return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, customer_group=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions, customer_group)
	ordered_items = frappe._dict(
		frappe.db.get_all(
			"Sales Order Item",
			{"prevdoc_docname": source_name, "docstatus": 1},
			["item_code", "sum(qty)"],
			group_by="item_code",
			as_list=1,
		)
	)
	

	selected_rows = [x.get("name") for x in frappe.flags.get("args", {}).get("selected_items", [])]

	def set_missing_values(source, target):
		if source.custom_sales_executive:
			target.append("sales_team",{
				"sales_person":source.custom_sales_executive,
				"allocated_percentage":100
			})
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		if source.referral_sales_partner:
			target.sales_partner = source.referral_sales_partner
			target.commission_rate = frappe.get_value(
				"Sales Partner", source.referral_sales_partner, "commission_rate"
			)

		# sales team
		if not target.get("sales_team"):
			for d in customer.get("sales_team") or []:
				target.append(
					"sales_team",
					{
						"sales_person": d.sales_person,
						"allocated_percentage": d.allocated_percentage or None,
						"commission_rate": d.commission_rate,
					},
				)

		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		balance_qty = obj.qty - ordered_items.get(obj.item_code, 0.0)
		target.qty = balance_qty if balance_qty > 0 else 0
		target.stock_qty = flt(target.qty) * flt(obj.conversion_factor)

		if obj.against_blanket_order:
			target.against_blanket_order = obj.against_blanket_order
			target.blanket_order = obj.blanket_order
			target.blanket_order_rate = obj.blanket_order_rate

	def can_map_row(item) -> bool:
		"""
		Row mapping from Quotation to Sales order:
		1. If no selections, map all non-alternative rows (that sum up to the grand total)
		2. If selections: Is Alternative Item/Has Alternative Item: Map if selected and adequate qty
		3. If selections: Simple row: Map if adequate qty
		"""
		has_qty = item.qty > 0

		if not selected_rows:
			return not item.is_alternative

		if selected_rows and (item.is_alternative or item.has_alternative_item):
			return (item.name in selected_rows) and has_qty

		# Simple row
		return has_qty

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {"doctype": "Sales Order", "validation": {"docstatus": ["=", 1]}},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {"parent": "prevdoc_docname", "name": "quotation_item"},
				"postprocess": update_item,
				"condition": can_map_row,
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
			"Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	return doclist				

def _make_customer(source_name, ignore_permissions=False, customer_group=None):
	quotation = frappe.db.get_value(
		"Quotation", source_name, ["order_type", "party_name", "customer_name"], as_dict=1
	)

	if quotation and quotation.get("party_name"):
		if not frappe.db.exists("Customer", quotation.get("party_name")):
			lead_name = quotation.get("party_name")
			customer_name = frappe.db.get_value(
				"Customer", {"lead_name": lead_name}, ["name", "customer_name"], as_dict=True
			)
			if not customer_name:
				from erpnext.crm.doctype.lead.lead import _make_customer

				customer_doclist = _make_customer(lead_name, ignore_permissions=ignore_permissions)
				customer = frappe.get_doc(customer_doclist)
				customer.flags.ignore_permissions = ignore_permissions
				customer.customer_group = customer_group

				try:
					customer.insert()
					return customer
				except frappe.NameError:
					if frappe.defaults.get_global_default("cust_master_name") == "Customer Name":
						customer.run_method("autoname")
						customer.name += "-" + lead_name
						customer.insert()
						return customer
					else:
						raise
				except frappe.MandatoryError as e:
					mandatory_fields = e.args[0].split(":")[1].split(",")
					mandatory_fields = [customer.meta.get_label(field.strip()) for field in mandatory_fields]

					frappe.local.message_log = []
					lead_link = frappe.utils.get_link_to_form("Lead", lead_name)
					message = (
						_("Could not auto create Customer due to the following missing mandatory field(s):")
						+ "<br>"
					)
					message += "<br><ul><li>" + "</li><li>".join(mandatory_fields) + "</li></ul>"
					message += _("Please create Customer from Lead {0}.").format(lead_link)

					frappe.throw(message, title=_("Mandatory Missing"))
			else:
				return customer_name
		else:
			return frappe.get_doc("Customer", quotation.get("party_name"))
