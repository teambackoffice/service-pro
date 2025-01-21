import frappe
from frappe.model.document import Document
from frappe import _
import json

from frappe.utils import (
	flt,
)



from erpnext.controllers.accounts_controller import set_order_defaults, validate_and_delete_children


class InterCompanyStockTransfer(Document):
    @frappe.whitelist()
    def get_avail_qty(self,item):
        bin = frappe.db.sql(""" SELECT * FROM `tabBin` WHERE item_code=%s and warehouse=%s """,(item['item_code'],self.from_warehouse),as_dict=1)
            
        return bin[0] if len(bin) > 0 else 0

@frappe.whitelist()
def reserve_material_transfer(name):
   
        doc = frappe.get_doc("Inter Company Stock Transfer", name)
        
        material_issue = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "posting_date": doc.posting_date,
            "posting_time": doc.time,
            "from_warehouse": doc.in_transit_warehouse,
            "company": doc.from_company,
            "items": []
        }
        for x in doc.item_details:
            material_issue["items"].append({
                "item_code": x.item_code,
                "qty": x.qty,
                "s_warehouse": doc.in_transit_warehouse,
                "basic_rate": x.value,
                "expense_account": doc.from_company_debit_account,
                "cost_center": doc.from_cost_center,
                "custom_inter_company_stock_transfer": x.parent
            })
        
        mi_doc = frappe.get_doc(material_issue)
        mi_doc.insert(ignore_permissions=True)
        mi_doc.submit()
        frappe.msgprint(_('Material Issue created successfully'))

        material_receipt = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "posting_date": doc.posting_date,
            "posting_time": doc.time,
            "to_warehouse": doc.to_warehouse,
            "company": doc.to_company,
            "items": []
        }
        for x in doc.item_details:
            material_receipt["items"].append({
                "item_code": x.item_code,
                "qty": x.received_qty,
                "basic_rate": x.credit_value,
                "expense_account": doc.to_company_credit_account,
                "cost_center": doc.to_cost_center,
                "custom_inter_company_stock_transfer": x.parent
            })

        mt_doc = frappe.get_doc(material_receipt)
        mt_doc.insert(ignore_permissions=True)
        mt_doc.submit()
        frappe.msgprint(_('Material Receipt created successfully'))

        doc.is_received = 1
        doc.status = "Received"
        doc.save(ignore_permissions=True)

        return {"message": "Stock Entries created successfully"}
    
    



	# @frappe.whitelist()
	# def get_defaults(self):
	# 	print("--------------------------------------------------------------------------")
	# 	defaults = {}

	# 	if self.from_company:
	# 		tables = [
	# 			"Inter Company Stock Transfer From",
	# 		]
	# 		for table in tables:
	# 			data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.from_company,
	# 								 as_dict=1)
	# 			if len(data) > 0:
	# 				defaults[data[0].parentfield] = data[0]

	# 		self.from_warehouse = defaults['from_companies'].warehouse if 'from_companies' in defaults else ""
	# 		self.from_company_debit_account = defaults['from_companies'].account if 'from_companies' in defaults else ""
	# 		self.from_cost_center = defaults['from_companies'].cost_center if 'from_companies' in defaults else ""

	# 	if self.to_company:
	# 		tables = [
	# 			"Inter Company Stock Transfer To",
	# 		]
	# 		for table in tables:
	# 			data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table), self.to_company,
	# 								 as_dict=1)
	# 			if len(data) > 0:
	# 				defaults[data[0].parentfield] = data[0]

	# 		self.to_warehouse = defaults['to_companies'].warehouse if 'to_companies' in defaults else ""
	# 		self.to_company_credit_account = defaults['to_companies'].account if 'to_companies' in defaults else ""
	# 		self.to_cost_center = defaults['to_companies'].cost_center if 'from_companies' in defaults else ""

	# 	return defaults


@frappe.whitelist()
def create_material_transfer(name):
    source_doc = frappe.get_doc("Inter Company Stock Transfer", name)

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.company = source_doc.from_company
    stock_entry.from_warehouse = source_doc.from_warehouse
    stock_entry.to_warehouse = source_doc.in_transit_warehouse

    for item in source_doc.item_details:
        stock_entry.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "basic_rate": item.value,
            "s_warehouse": source_doc.from_warehouse,
            "t_warehouse": source_doc.in_transit_warehouse,
            "cost_center": source_doc.from_cost_center,
            "custom_inter_company_stock_transfer": item.parent
        })

    stock_entry.insert()
    stock_entry.submit()

    frappe.db.set_value("Inter Company Stock Transfer", name, "in_transit", 1, update_modified=False)
    frappe.db.set_value("Inter Company Stock Transfer", name, "status","In Transit")
    frappe.db.commit()

    return stock_entry.name


@frappe.whitelist()
def update_child_qty_rate(parent_doctype, trans_items, parent_doctype_name, child_docname="item_details"):
    print(trans_items)
    print(parent_doctype_name)
    print(child_docname)
    data = json.loads(trans_items)
    parent = frappe.get_doc(parent_doctype, parent_doctype_name)
    
    def get_new_child_item(item_row):
        child_doctype = "Inter Company Stock Transfer Item"
        return set_order_defaults(parent_doctype, parent_doctype_name, child_doctype, child_docname, item_row)
    
    def set_order_defaults(parent_doctype, parent_doctype_name, child_doctype, child_docname, trans_item):
        """
        Returns a Sales/Purchase Order Item child item containing the default values
		"""
        p_doc = frappe.get_doc(parent_doctype, parent_doctype_name)
        child_item = frappe.new_doc(child_doctype, parent_doc=p_doc, parentfield=child_docname)
        item = frappe.get_doc("Item", trans_item.get("item_code"))
        for field in ("item_code", "item_name"):
            child_item.update({field: item.get(field)})
        child_item.available_qty = trans_item.get("available_qty")
        child_item.qty = trans_item.get("qty")
        child_item.received_qty = trans_item.get("received_qty")
        child_item.value = trans_item.get("value")
        child_item.credit_value = trans_item.get("credit_value")
        return child_item
    for d in data:
        new_child_flag = False
        if not d.get("item_code"):
            continue
        if not d.get("docname"):
            new_child_flag = True
            items_added_or_removed = True
            check_doc_permissions(parent, "create")
            child_item = get_new_child_item(d)
        else:
            check_doc_permissions(parent, "write")
            child_item = frappe.get_doc("Inter Company Stock Transfer Item", d.get("docname"))
            prev_available_qty, new_available_qty = flt(child_item.get("available_qty")), flt(d.get("available_qty"))
            prev_qty, new_qty = flt(child_item.get("qty")), flt(d.get("qty"))
            prev_received_qty, new_received_qty = flt(child_item.get("received_qty")), flt(d.get("received_qty"))
            prev_value, new_value = flt(child_item.get("value")), flt(d.get("value"))
            prev_credit_value, new_credit_value = flt(child_item.get("credit_value")), flt(d.get("credit_value"))
            if prev_available_qty != new_available_qty:
                child_item.available_qty = new_available_qty
            if prev_qty != new_qty:
                child_item.qty = new_qty
            if prev_received_qty != new_received_qty:
                child_item.received_qty = new_received_qty
        child_item.flags.ignore_validate_update_after_submit = True
        if new_child_flag:
            parent.load_from_db()
            child_item.idx = len(parent.item_details) + 1
            child_item.insert()
        else:
            child_item.save()
    parent.reload()
    parent.flags.ignore_validate_update_after_submit = True
    for idx, row in enumerate(parent.get(child_docname), start=1):
        row.idx = idx
    parent.save()
    parent.reload()
            

def check_doc_permissions(doc, perm_type="create"):
	try:
		doc.check_permission(perm_type)
	except frappe.PermissionError:
		actions = {"create": "add", "write": "update"}

		frappe.throw(
			_("You do not have permissions to {} items in a {}.").format(
				actions[perm_type], doc.doctype
			),
			title=_("Insufficient Permissions"),
		)

