from frappe.model.document import Document
import frappe
from frappe import _

class InterCompanyMaterialRequest(Document):
    def validate(self):
        for item in self.items:
            item_qty = float(item.qty) if isinstance(item.qty, (int, float, str)) and item.qty else 0
            item_available_qty = float(item.available_qty) if isinstance(item.available_qty, (int, float, str)) and item.available_qty else 0
            company = frappe.db.get_value("Inter Company Stock Transfer Template", {"name": item.stock_transfer_template}, "from_company")
            if company != "HYDROTECH COMPANY CENTRAL WAREHOUSE":
                if item_qty > item_available_qty:
                    frappe.throw(
                        _("The requested quantity for Item {0} exceeds the available quantity or is not available in the required warehouse.")
                        .format(item.item_code)
                    )

        # Check material request type for central warehouse templates
        for item in self.items:
            if item.stock_transfer_template:
                from_company = frappe.db.get_value("Inter Company Stock Transfer Template", 
                    item.stock_transfer_template, "from_company")
                
                if from_company == "HYDROTECH COMPANY CENTRAL WAREHOUSE" and \
                    self.material_request_type != "Purchase":
                    frappe.throw(
                        _("When selecting a template from Central Warehouse, Material Request Type must be 'Purchase'")
                    )
                elif from_company != "HYDROTECH COMPANY CENTRAL WAREHOUSE" and \
                    self.material_request_type != "Material Transfer":
                    frappe.throw(
                        _("When selecting a template from other warehouses, Material Request Type must be 'Material Transfer'")
                    )

    def on_submit(self):
        stock_transfer = frappe.new_doc("Inter Company Stock Transfer")

        total_qty = 0
        debit_value = 0
        credit_value = 0

        # Ensure at least one valid template is present
        for item in self.items:
            if not item.stock_transfer_template:
                frappe.throw(_("No stock transfer template found for item {0}.").format(item.item_code))

            # Set template only once; assume all items use same template
            if not stock_transfer.template:
                stock_transfer.template = item.stock_transfer_template

        stock_transfer.inter_company_material_request = self.name

        # Append items and compute totals
        for item in self.items:
            # Get the from_company from the stock transfer template
            from_company = frappe.db.get_value("Inter Company Stock Transfer Template", 
                item.stock_transfer_template, "from_company")
            
            # Only validate quantity if NOT from HYDROTECH COMPANY CENTRAL WAREHOUSE
            if from_company != "HYDROTECH COMPANY CENTRAL WAREHOUSE":
                if float(item.qty) > float(item.available_qty):
                    frappe.throw(_("Qty of {0} cannot be more than available qty.").format(item.item_code))

            total_qty += float(item.qty)
            debit_value += float(item.rate)
            credit_value += float(item.rate)

            stock_transfer.append("item_details", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "value": item.rate,
                "credit_value": item.rate,
                "available_qty": item.available_qty,
                "qty": item.qty,
                "received_qty": item.qty
            })

        # Set computed totals
        stock_transfer.total_qty = total_qty
        stock_transfer.debit_value = debit_value
        stock_transfer.credit_value = credit_value
        stock_transfer.deference_value = debit_value - credit_value

        stock_transfer.insert()
        frappe.msgprint(_("Inter Company Stock Transfer {0} has been created.").format(stock_transfer.name))
       

        
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
    """Get available quantity for an item across all warehouses"""
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
    """Get available quantity for specific template warehouse"""
    template = frappe.get_doc("Inter Company Stock Transfer Template", stock_transfer_template)

    available_qty = frappe.db.get_value(
        "Bin",
        {"item_code": item_code, "warehouse": template.from_warehouse, "actual_qty": ['!=', 0]},
        "actual_qty"
    )

    return available_qty or 0


@frappe.whitelist()
def get_valution_rate(item_code):
    """Get valuation rate for an item (legacy method)"""
    valuation_rate = frappe.db.get_value(
        "Bin",
        {"item_code": item_code},
        "valuation_rate"
    )

    return valuation_rate or 0


@frappe.whitelist()
def get_warehouse_valuation_rate(item_code, warehouse):
    """Get warehouse-specific valuation rate for an item"""
    if not item_code or not warehouse:
        return 0
        
    # Get valuation rate from Bin for specific item-warehouse combination
    valuation_rate = frappe.db.get_value(
        "Bin",
        {
            "item_code": item_code,
            "warehouse": warehouse
        },
        "valuation_rate"
    )
    
    if valuation_rate:
        return float(valuation_rate)
    else:
        # If no Bin record exists for this warehouse, try to get standard rate from Item
        standard_rate = frappe.db.get_value(
            "Item",
            item_code,
            "standard_rate"
        )
        return float(standard_rate) if standard_rate else 0