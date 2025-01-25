from frappe.model.document import Document
import frappe
from frappe import _

class InterCompanyMaterialRequest(Document):
    def validate(self):
        for item in self.items:
            item_qty = float(item.qty) if isinstance(item.qty, (int, float, str)) and item.qty else 0
            item_available_qty = float(item.available_qty) if isinstance(item.available_qty, (int, float, str)) and item.available_qty else 0
            if item_qty > item_available_qty:
                frappe.throw(
                    _("The requested quantity for Item {0} exceeds the available quantity.").format(item.item_code)
                    )


    def on_submit(self):
        stock_transfer = frappe.new_doc("Inter Company Stock Transfer")
        for item in self.get("items"):
            if not item.stock_transfer_template:
                frappe.throw("No stock transfer template found in items.")
        
            stock_transfer.template = item.stock_transfer_template

        stock_transfer.inter_company_material_request = self.name

        
        for item in self.get("items"):
            stock_transfer.append("item_details", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "value": item.rate,
                "available_qty": item.available_qty,
                "qty": item.qty,
                "received_qty": item.qty
            })
        
        stock_transfer.insert()
       

        
#     def on_submit(self):
#         create_material_requests(self)

# def create_material_requests(doc):
#     """
#     Create Material Requests grouped by supplier from the Inter Company Material Request.
#     """
#     supplier_items_map = {}
#     for item in doc.items: 
#         if not item.supplier:
#             frappe.throw(f"Supplier is missing for item {item.item_code}. Please provide a valid supplier.")
        
#         if item.supplier not in supplier_items_map:
#             supplier_items_map[item.supplier] = []
#         supplier_items_map[item.supplier].append(item)

#     for supplier, items in supplier_items_map.items():
#         supplier_name = frappe.db.get_value("Supplier", supplier, "supplier_name")
        
#         material_request = frappe.new_doc("Material Request")
#         material_request.update({
#             "company": doc.company,  
#             "internal_supplier": supplier, 
#             "custom_internal_supplier_name": supplier_name, 
#             "material_request_type": "Purchase",
#             "custom_inter_company_material_request": doc.name,
#             "set_warehouse": doc.set_warehouse,
#             "items": []
#         })

#         for item in items:
#             material_request.append("items", {
#                 "item_code": item.item_code,
#                 "warehouse": doc.set_warehouse,
#                 "qty": item.qty,
#                 "schedule_date": doc.schedule_date or frappe.utils.nowdate()
#             })

#         material_request.save()
#         frappe.msgprint(f"Material Request {material_request.name} created for supplier {supplier} ({supplier_name})")




@frappe.whitelist()
def get_available_qty(item_code):
    warehouses = frappe.db.sql(
        """
        SELECT 
            wh.name AS warehouse,
            wh.company,
            bin.item_code,
            bin.actual_qty,
            item.item_name 
        FROM 
            `tabWarehouse` AS wh
        LEFT JOIN 
            `tabBin` AS bin
        ON 
            wh.name = bin.warehouse
        LEFT JOIN 
            `tabItem` AS item
        ON 
            bin.item_code = item.name
        WHERE 
            bin.item_code = %s
        """,
        (item_code,),
        as_dict=True
    )
    return warehouses


@frappe.whitelist()
def get_available(item_code, stock_transfer_template):
    templete = frappe.get_doc("Inter Company Stock Transfer Template", stock_transfer_template)

    available_qty = frappe.db.get_value(
        "Bin",
        {"item_code": item_code, "warehouse": templete.from_warehouse},
        "actual_qty"
    )

    return available_qty or 0


@frappe.whitelist()
def get_valution_rate(item_code):

    available_qty = frappe.db.get_value(
        "Bin",
        {"item_code": item_code},
        "valuation_rate"
    )

    return available_qty