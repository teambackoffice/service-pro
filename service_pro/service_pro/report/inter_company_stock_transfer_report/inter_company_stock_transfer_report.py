# ERPNext Script Report for "Inter Company Stock Transfer"
# Doctype: Inter Company Stock Transfer
# Child Table: item_details (fields: item_code, qty, value)

import frappe

# def execute(filters=None):
#     columns = [
#         {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
#         {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 250},
#         {"label": "Item", "fieldname": "from_item", "fieldtype": "Data", "width": 120},
#         {"label": "Issued Qty", "fieldname": "from_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Debit Value", "fieldname": "from_value", "fieldtype": "Currency", "width": 100},
#         {"label": "Total", "fieldname": "from_total", "fieldtype": "Currency", "width": 100},
#         {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 250},
#         {"label": "Item", "fieldname": "to_item", "fieldtype": "Data", "width": 120},
#         {"label": "Received Qty", "fieldname": "to_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Credit Value", "fieldname": "to_value", "fieldtype": "Currency", "width": 100},
#          {"label": "Total", "fieldname": "to_total", "fieldtype": "Currency", "width": 100},
#         {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
#         {"label": "Value Diff", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
#         {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
#         {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
#     ]

#     data = []

#     transfers = frappe.get_all("Inter Company Stock Transfer",
#     filters={
#         **{k: v for k, v in filters.items() if k in ["from_company", "to_company", "name", "status"]},  # Only non-date filters
#         "posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
#     },
#     fields=["name", "from_company", "to_company", "status", "posting_date"]
# )

#     for transfer in transfers:
#         debit_value = frappe.get_value("Inter Company Stock Transfer", transfer.name, "debit_value")
#         credit_value = frappe.get_value("Inter Company Stock Transfer", transfer.name, "credit_value")

      
#         if debit_value is None:
#             debit_value = 0  
#         if credit_value is None:
#             credit_value = 0 

#         items = frappe.get_all("Inter Company Stock Transfer Item",
#             filters={"parent": transfer.name},
#             fields=["item_code", "qty", "value", "received_qty", "credit_value"]
#         )

#         for item in items:
#             qty_diff = item.qty - item.received_qty
#             value_diff = item.value - item.credit_value
#             data.append({
#                 "name": transfer.name,
#                 "from_company": transfer.from_company,
#                 "from_item": item.item_code,  
#                 "from_qty": item.qty,
#                 "from_value": item.value,
#                 "from_total": debit_value,
#                 "to_company": transfer.to_company,
#                 "to_item": item.item_code,  
#                 "to_qty": item.received_qty,  
#                 "to_value": item.credit_value,
#                 "to_total": credit_value, 
#                 "qty_diff": qty_diff,
#                 "value_diff": value_diff,
#                 "status": transfer.status,
#                 "posting_date": transfer.posting_date
#             })

#     return columns, data
# import frappe

# def execute(filters=None):
#     columns = [
#         {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
#         {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 200},
#         {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 200},
#         {"label": "Item", "fieldname": "item_code", "fieldtype": "Data", "width": 120},
#         {"label": "Issued Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "Value", "fieldname": "value", "fieldtype": "Currency", "width": 100},
#         {"label": "Received Qty", "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Credit Value", "fieldname": "credit_value", "fieldtype": "Currency", "width": 100},
#         {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
#         {"label": "Value Diff", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
#         {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
#         {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
#         {"label": "group_id", "fieldname": "group_id", "fieldtype": "Data", "hidden": 1}
#     ]

#     data = []

#     # Apply filters
#     conditions = {}
#     for key in ["from_company", "to_company", "name", "status"]:
#         if filters.get(key):
#             conditions[key] = filters[key]

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]

#     transfers = frappe.get_all(
#         "Inter Company Stock Transfer",
#         filters=conditions,
#         fields=["name", "from_company", "to_company", "status", "posting_date"]
#     )

#     for transfer in transfers:
#         items = frappe.get_all(
#             "Inter Company Stock Transfer Item",
#             filters={"parent": transfer.name},
#             fields=["item_code", "qty", "value", "received_qty", "credit_value"]
#         )

#         first = True
#         for item in items:
#             data.append({
#                 "name": transfer.name if first else "",
#                 "from_company": transfer.from_company if first else "",
#                 "to_company": transfer.to_company if first else "",
#                 "item_code": item.item_code,
#                 "qty": item.qty,
#                 "value": item.value,
#                 "received_qty": item.received_qty,
#                 "credit_value": item.credit_value,
#                 "qty_diff": (item.qty or 0) - (item.received_qty or 0),
#                 "value_diff": (item.value or 0) - (item.credit_value or 0),
#                 "status": transfer.status if first else "",
#                 "posting_date": transfer.posting_date if first else "",
#                 "group_id": transfer.name
#             })
#             first = False

#     return columns, data

# def execute(filters=None):
#     columns = [
#         {"label": "Transfer ID", "fieldname": "name", "fieldtype": "Data", "width": 180},
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
#         {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 200},
#         {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 200},
#     ]

#     data = []

#     transfers = frappe.get_all(
#         "Inter Company Stock Transfer",
#         filters=filters,
#         fields=["name", "from_company", "to_company"]
#     )

#     for t in transfers:
#         # Parent Row
#         data.append({
#             "name": t.name,
#             "item_code": "",
#             "qty": "",
#             "from_company": t.from_company,
#             "to_company": t.to_company,
#             "indent": 0
#         })

#         # Child Rows
#         items = frappe.get_all(
#             "Inter Company Stock Transfer Item",
#             filters={"parent": t.name},
#             fields=["item_code", "qty"]
#         )

#         for item in items:
#             data.append({
#                 "name": item.item_code + "-" + t.name,  # unique name for child
#                 "parent_transfer": t.name,
#                 "item_code": item.item_code,
#                 "qty": item.qty,
#                 "from_company": "",
#                 "to_company": "",
#                 "indent": 1
#             })

#     return columns, data

# def add_items_by_id(transfer_id):
#     items = frappe.get_all("Inter Company Stock Transfer Item",
#         filters={"parent": transfer_id},
#         fields=["item_code", "qty", "value"]
#     )
    
#     dropdown_items = [{"label": item.item_code, "value": item.item_code} for item in items]
    
#     return dropdown_items
def execute(filters=None):
    columns = [
        {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 200},
        {"label": "From Item", "fieldname": "from_item", "fieldtype": "Data", "width": 120},
        {"label": "Issued Qty", "fieldname": "from_qty", "fieldtype": "Float", "width": 100},
        {"label": "Debit Rate", "fieldname": "from_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total Debit", "fieldname": "from_total", "fieldtype": "Currency", "width": 100},
        {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 200},
        {"label": "To Item", "fieldname": "to_item", "fieldtype": "Data", "width": 120},
        {"label": "Received Qty", "fieldname": "to_qty", "fieldtype": "Float", "width": 100},
        {"label": "Credit Rate", "fieldname": "to_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total Credit", "fieldname": "to_total", "fieldtype": "Currency", "width": 100},
        {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
        {"label": "Value Diff", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100}
    ]

    data = []
    total_issued_qty = total_received_qty = total_debit = total_credit = 0

    transfers = frappe.get_all(
        "Inter Company Stock Transfer",
        filters={
            **{k: v for k, v in (filters or {}).items() if k in ["from_company", "to_company", "status"]},
            "posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]] if filters else ["!=", ""]
        },
        fields=["name", "from_company", "to_company", "status", "posting_date"]
    )

    for transfer in transfers:
        items = frappe.get_all(
            "Inter Company Stock Transfer Item",
            filters={"parent": transfer.name},
            fields=["item_code", "qty", "value", "received_qty", "credit_value"]
        )

        # Add parent row (Transfer Header)
        data.append({
            "name": transfer.name,
            "from_company": transfer.from_company,
            "to_company": transfer.to_company,
            "status": transfer.status,
            "posting_date": transfer.posting_date,
            "indent": 0
        })

        for item in items:
            from_total = (item.qty or 0) * (item.value or 0)
            to_total = (item.received_qty or 0) * (item.credit_value or 0)
            qty_diff = (item.qty or 0) - (item.received_qty or 0)
            value_diff = from_total - to_total

            data.append({
                "name": f"{transfer.name}-{item.item_code}",
                "from_item": item.item_code,
                "from_qty": item.qty,
                "from_value": item.value,
                "from_total": from_total,
                "to_item": item.item_code,
                "to_qty": item.received_qty,
                "to_value": item.credit_value,
                "to_total": to_total,
                "qty_diff": qty_diff,
                "value_diff": value_diff,
                "indent": 1
            })

            total_issued_qty += item.qty or 0
            total_received_qty += item.received_qty or 0
            total_debit += from_total
            total_credit += to_total

    # Append totals row
    data.append({
        "name": "TOTAL",
        "from_qty": total_issued_qty,
        "to_qty": total_received_qty,
        "from_total": total_debit,
        "to_total": total_credit,
        "indent": 0
    })

    return columns, data
