# ERPNext Script Report for "Inter Company Stock Transfer"
# Doctype: Inter Company Stock Transfer
# Child Table: item_details (fields: item_code, qty, value)

import frappe

def execute(filters=None):
    columns = [
        {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 250},
        {"label": "Item", "fieldname": "from_item", "fieldtype": "Data", "width": 120},
        {"label": "Issued Qty", "fieldname": "from_qty", "fieldtype": "Float", "width": 100},
        {"label": "Debit Value", "fieldname": "from_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total", "fieldname": "from_total", "fieldtype": "Currency", "width": 100},
        {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 250},
        {"label": "Item", "fieldname": "to_item", "fieldtype": "Data", "width": 120},
        {"label": "Received Qty", "fieldname": "to_qty", "fieldtype": "Float", "width": 100},
        {"label": "Credit Value", "fieldname": "to_value", "fieldtype": "Currency", "width": 100},
         {"label": "Total", "fieldname": "to_total", "fieldtype": "Currency", "width": 100},
        {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
        {"label": "Value Diff", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
    ]

    data = []

    transfers = frappe.get_all("Inter Company Stock Transfer",
    filters={
        **{k: v for k, v in filters.items() if k in ["from_company", "to_company", "name", "status"]},  # Only non-date filters
        "posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
    },
    fields=["name", "from_company", "to_company", "status", "posting_date"]
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
            qty_diff = item.qty - item.received_qty
            value_diff = item.value - item.credit_value
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
                "qty_diff": qty_diff,
                "value_diff": value_diff,
                "status": transfer.status,
                "posting_date": transfer.posting_date
            })

    return columns, data

def add_items_by_id(transfer_id):
    items = frappe.get_all("Inter Company Stock Transfer Item",
        filters={"parent": transfer_id},
        fields=["item_code", "qty", "value"]
    )
    
    dropdown_items = [{"label": item.item_code, "value": item.item_code} for item in items]
    
    return dropdown_items
