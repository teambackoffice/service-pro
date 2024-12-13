import frappe
from frappe.model.document import Document
from frappe import _
import json

from frappe.utils import (
	flt,
)



from erpnext.controllers.accounts_controller import set_order_defaults, validate_and_delete_children


class InterCompanyStockTransfer(Document):
    def first_se(self):
        obj = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "posting_date": self.posting_date,
            "posting_time": self.time,
            "from_warehouse": self.from_warehouse,
            "company": self.from_company,
            "set_posting_time": 1
        }

        items = []
        for x in self.item_details:
            items.append({
                "item_code": x.item_code,
                "qty": x.qty,
                "s_warehouse": self.in_transit_warehouse,
                "basic_rate": x.value,
                "expense_account": self.from_company_debit_account,
                "cost_center": self.from_cost_center,
                "custom_inter_company_stock_transfer": x.parent
            })

        obj['items'] = items
        se = frappe.get_doc(obj).insert(ignore_permissions=True)
        frappe.msgprint(_('Material Issue created successfully'))
        se.submit()

    def second_se(self):
        obj = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "posting_date": self.posting_date,
            "posting_time": self.time,
            "to_warehouse": self.to_warehouse,
            "company": self.to_company,
        }

        items = []
        for x in self.item_details:
            items.append({
                "item_code": x.item_code,
                "qty": x.received_qty,
                "s_warehouse": self.from_warehouse,
                "basic_rate": x.credit_value,
                "expense_account": self.to_company_credit_account,
                "cost_center": self.to_cost_center,
                "custom_inter_company_stock_transfer": x.parent
            })

        obj['items'] = items
        se = frappe.get_doc(obj).insert(ignore_permissions=True)
        frappe.msgprint(_('Material Receipt created successfully'))
        se.submit()
        
    @frappe.whitelist()
    def get_avail_qty(self,item):
        bin = frappe.db.sql(""" SELECT * FROM `tabBin` WHERE item_code=%s and warehouse=%s """,(item['item_code'],self.from_warehouse),as_dict=1)
            
        return bin[0] if len(bin) > 0 else 0

@frappe.whitelist()
def reserve_material_transfer(name):
    """Function to create both stock entries and mark the transfer as received."""
    doc = frappe.get_doc("Inter Company Stock Transfer", name)
    doc.first_se()
    doc.second_se()
    frappe.db.set_value("Inter Company Stock Transfer", name, "is_received", 1, update_modified=False)
    frappe.db.set_value("Inter Company Stock Transfer", name, "status","Received")
    frappe.db.commit()
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

