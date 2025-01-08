import frappe
from frappe.utils.data import add_to_date, get_time, getdate
from pyqrcode import create as qr_create
import io
from frappe import _ 
import os
from base64 import b64encode
from datetime import datetime
from erpnext import get_region
from frappe.model.mapper import get_mapped_doc

# def on_so_submit(doc, method=None):
# 	if doc.selling_price_list:
# 		if frappe.db.exists("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}):
# 			max_disc = frappe.db.get_value("Maximum User Discount", {"parent":doc.selling_price_list, "user": frappe.session.user}, ["max_discount"])
# 			over_disc = frappe.db.exists("Sales Order Item", {"parent":doc.name, "discount_percentage": [">", max_disc]}, ['item_code'])
# 			if max_disc and over_disc:
# 				frappe.throw("Maximum allowed discount is {0} for item {1}".format(max_disc, frappe.db.get_value("Sales Order Item", over_disc, ['item_code'])))
	
# 	if doc.custom_production:
# 		for prod in doc.custom_production:
# 			if prod.reference:
# 				pd = frappe.get_doc("Production",prod.reference)
# 				if prod.qty <= pd.qty:
# 					frappe.db.set_value("Production", prod.reference, "status", "Partially Sales Order")
# 					frappe.db.commit()

# 				else:
# 					frappe.db.set_value("Production", prod.reference, "status", "Completed")
# 					frappe.db.commit()
@frappe.whitelist()
def sales_order_submit(doc, method):
	frappe.db.set_value('Service Order Form', doc.custom_service_order_form_id, 'status', 'Converted')
	
	frappe.db.commit()


# @frappe.whitelist()
# def make_sales_order_from_service_order(source_name, target_doc=None):
#     doclist = get_mapped_doc(
#         "Sales Order",
#         source_name,
#         {
#             "Sales Order": {
#                 "doctype": "Service Order Form",
#                 "field_map": {
#                     "customer": "customer",
                   
#                 }
#             }
#         },
#         target_doc,
#     )

#     return doclist

def create_qr_code(doc, method=None):
	region = get_region(doc.company)
	if region not in ["Saudi Arabia"]:
		return



	# Don't create QR Code if it already exists
	qr_code = doc.get("ksa_einv_qr")
	if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
		return

	meta = frappe.get_meta(doc.doctype)

	if "ksa_einv_qr" in [d.fieldname for d in meta.get_image_fields()]:
		"""TLV conversion for
		1. Seller's Name
		2. VAT Number
		3. Time Stamp
		4. Invoice Amount
		5. VAT Amount
		"""
		tlv_array = []
		# Sellers Name

		seller_name = frappe.db.get_value("Company", doc.company, "company_name_in_arabic")

		if not seller_name:
			frappe.throw(_("Arabic name missing for {} in the company document").format(doc.company))

		tag = bytes([1]).hex()
		length = bytes([len(seller_name.encode("utf-8"))]).hex()
		value = seller_name.encode("utf-8").hex()
		tlv_array.append("".join([tag, length, value]))

		# VAT Number
		tax_id = frappe.db.get_value("Company", doc.company, "tax_id")
		if not tax_id:
			frappe.throw(_("Tax ID missing for {} in the company document").format(doc.company))

		tag = bytes([2]).hex()
		length = bytes([len(tax_id)]).hex()
		value = tax_id.encode("utf-8").hex()
		tlv_array.append("".join([tag, length, value]))

		# Time Stamp
		delivery_datetime = datetime.combine(getdate(doc.delivery_date), datetime.min.time())
		specific_time = delivery_datetime.replace(hour=8, minute=0, second=0)
		time_stamp = specific_time.strftime("%Y-%m-%dT%H:%M:%SZ")
		tag = bytes([3]).hex()
		length = bytes([len(time_stamp)]).hex()
		value = time_stamp.encode("utf-8").hex()
		tlv_array.append("".join([tag, length, value]))

		# Invoice Amount
		invoice_amount = str(doc.base_grand_total)
		tag = bytes([4]).hex()
		length = bytes([len(invoice_amount)]).hex()
		value = invoice_amount.encode("utf-8").hex()
		tlv_array.append("".join([tag, length, value]))

		# VAT Amount
		vat_amount = str(get_vat_amount(doc))

		tag = bytes([5]).hex()
		length = bytes([len(vat_amount)]).hex()
		value = vat_amount.encode("utf-8").hex()
		tlv_array.append("".join([tag, length, value]))

		# Joining bytes into one
		tlv_buff = "".join(tlv_array)

		# base64 conversion for QR Code
		base64_string = b64encode(bytes.fromhex(tlv_buff)).decode()

		qr_image = io.BytesIO()
		url = qr_create(base64_string, error="L")
		url.png(qr_image, scale=2, quiet_zone=1)

		name = frappe.generate_hash(doc.name, 5)

		# making file
		filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
		_file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": filename,
				"is_private": 0,
				"content": qr_image.getvalue(),
				"attached_to_doctype": doc.get("doctype"),
				"attached_to_name": doc.get("name"),
				"attached_to_field": "ksa_einv_qr",
			}
		)

		_file.save()

		# assigning to document
		doc.db_set("ksa_einv_qr", _file.file_url)
		doc.notify_update()


def get_vat_amount(doc):
	vat_settings = frappe.db.get_value("KSA VAT Setting", {"company": doc.company})
	vat_accounts = []
	vat_amount = 0

	if vat_settings:
		vat_settings_doc = frappe.get_cached_doc("KSA VAT Setting", vat_settings)

		for row in vat_settings_doc.get("ksa_vat_sales_accounts"):
			vat_accounts.append(row.account)

	for tax in doc.get("taxes"):
		if tax.account_head in vat_accounts:
			vat_amount += tax.base_tax_amount

	return vat_amount

def validate_permission(doc, method):
	if not doc.custom_ignore_permission_ and not doc.custom_production_id:
		frappe.throw("Quotation is Required")

@frappe.whitelist()
def get_role():
	doc = frappe.db.get_value("Production Settings",None,"ignore_permission")
	return doc