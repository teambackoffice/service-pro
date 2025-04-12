# ERPNext Script Report for "Inter Company Stock Transfer"
# Doctype: Inter Company Stock Transfer
# Child Table: item_details (fields: item_code, qty, value)

import frappe

def execute(filters=None):
    columns = [
        {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 150},
        {"label": "Item", "fieldname": "from_item", "fieldtype": "Data", "width": 120},
        {"label": "Qty", "fieldname": "from_qty", "fieldtype": "Float", "width": 80},
        {"label": "Value", "fieldname": "from_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total", "fieldname": "from_total", "fieldtype": "Currency", "width": 100},
        {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 150},
        {"label": "Item", "fieldname": "to_item", "fieldtype": "Data", "width": 120},
        {"label": "Qty", "fieldname": "to_qty", "fieldtype": "Float", "width": 80},
        {"label": "Value", "fieldname": "to_value", "fieldtype": "Currency", "width": 100},
         {"label": "Total", "fieldname": "to_total", "fieldtype": "Currency", "width": 100},
        {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
        {"label": "Value Diff", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
    ]

    data = []

    transfers = frappe.get_all("Inter Company Stock Transfer",
        filters=filters,
        fields=["name", "from_company", "to_company"]
    )
    for transfer in transfers:
        debit_value = frappe.get_value("Inter Company Stock Transfer", transfer.name, "debit_value")
        credit_value = frappe.get_value("Inter Company Stock Transfer", transfer.name, "credit_value")

      
        if debit_value is None:
            debit_value = 0  
        if credit_value is None:
            credit_value = 0 

        items = frappe.get_all("Inter Company Stock Transfer Item",
            filters={"parent": transfer.name},
            fields=["item_code", "qty", "value", "received_qty", "credit_value"]
        )

        for item in items:
            data.append({
                "name": transfer.name,
                "from_company": transfer.from_company,
                "from_item": item.item_code,  
                "from_qty": item.qty,
                "from_value": item.value,
                "from_total": debit_value,
                "to_company": transfer.to_company,
                "to_item": item.item_code,  
                "to_qty": item.received_qty,  
                "to_value": item.credit_value,
                "to_total": credit_value, 
                "qty_diff": 0, 
                "value_diff": 0  
            })

    return columns, data

def add_items_by_id(transfer_id):
    items = frappe.get_all("Inter Company Stock Transfer Item",
        filters={"parent": transfer_id},
        fields=["item_code", "qty", "value"]
    )
    
    dropdown_items = [{"label": item.item_code, "value": item.item_code} for item in items]
    
    return dropdown_items
