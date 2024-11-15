import frappe
from frappe.model.document import Document

class InterCompanyMaterialRequest(Document):
    def on_submit(self):
        create_material_requests(self)

def create_material_requests(doc):
    """
    Create Material Requests grouped by company from the Inter Company Material Request.
    """
    # Group items by company
    company_items_map = {}
    for item in doc.items:  # Assuming the child table is named 'items'
        if item.company not in company_items_map:
            company_items_map[item.company] = []
        company_items_map[item.company].append(item)

    # Create Material Request for each company
    for company, items in company_items_map.items():
        material_request = frappe.new_doc("Material Request")
        material_request.update({
            "company": company,
            "material_request_type": "Purchase",  # Or set it dynamically if needed
            "items": []
        })

        for item in items:
            material_request.append("items", {
                "item_code": item.item_code,
                "warehouse": item.warehouse,
                "qty": item.qty,
                "schedule_date": item.schedule_date or frappe.utils.nowdate()  # Default to today's date if not provided
            })

        # Save and optionally submit the Material Request
        material_request.save()
        frappe.msgprint(f"Material Request {material_request.name} created for company {company}")

@frappe.whitelist()
def get_available_qty(item_code):
    warehouses = frappe.db.sql("""
        SELECT
            sle.company AS company,
            sle.item_code AS item_code,
            item.item_name AS item_name,
            sle.warehouse AS warehouse,
            SUM(sle.actual_qty) AS actual_qty
        FROM
            `tabStock Ledger Entry` sle
        JOIN
            `tabItem` item ON sle.item_code = item.item_code
        WHERE
            sle.item_code = %s
        GROUP BY
            sle.company, sle.item_code, sle.warehouse
        ORDER BY
            sle.company, sle.warehouse
    """, (item_code,), as_dict=True)
    return warehouses
