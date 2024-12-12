import frappe
from frappe.model.document import Document
from frappe import _
import json


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
                "qty": x.received_qty,
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
            "s_warehouse": source_doc.from_warehouse,
            "t_warehouse": source_doc.in_transit_warehouse,
            "cost_center": source_doc.from_cost_center,
            "custom_inter_company_stock_transfer": item.parent
        })

    stock_entry.insert()
    stock_entry.submit()

    frappe.db.set_value("Inter Company Stock Transfer", name, "in_transit", 1, update_modified=False)

    return stock_entry.name

@frappe.whitelist()
def update_received_qty(docname, items):
    items = json.loads(items)
    doc = frappe.get_doc("Inter Company Stock Transfer", docname)

    doc.flags.ignore_validate_update_after_submit = True

    for item in doc.item_details:
        for updated_item in items:
            if item.item_code == updated_item.get("item_code"):
                item.received_qty = updated_item.get("received_qty")

    doc.save(ignore_permissions=True)  
    frappe.db.commit() 
    return doc.name




