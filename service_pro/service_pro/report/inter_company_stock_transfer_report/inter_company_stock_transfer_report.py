import frappe

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

    # Prepare filters
    transfer_filters = {
        key: val for key, val in (filters or {}).items()
        if key in ["from_company", "to_company", "status", "name", "posting_date"]
    }

    # Range filter
    if filters and filters.get("from_date") and filters.get("to_date"):
        transfer_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]

    # Fetch transfer documents
    transfers = frappe.get_all(
        "Inter Company Stock Transfer",
        filters=transfer_filters,
        fields=["name", "from_company", "to_company", "status", "posting_date"]
    )

    for transfer in transfers:
        # Parent row
        data.append({
            "name": transfer.name,
            "from_company": transfer.from_company,
            "to_company": transfer.to_company,
            "status": transfer.status,
            "posting_date": transfer.posting_date,
            "indent": 0
        })

        # Child items
        items = frappe.get_all(
            "Inter Company Stock Transfer Item",
            filters={"parent": transfer.name},
            fields=["item_code", "qty", "value", "received_qty", "credit_value"]
        )

        for item in items:
            qty = item.get("qty") or 0
            value = item.get("value") or 0
            received_qty = item.get("received_qty") or 0
            credit_value = item.get("credit_value") or 0

            from_total = qty * value
            to_total = received_qty * credit_value
            qty_diff = qty - received_qty
            value_diff = from_total - to_total

            data.append({
                "name": f"{transfer.name}-{item.item_code}",
                "parent_transfer": transfer.name,
                "from_item": item.item_code,
                "from_qty": qty,
                "from_value": value,
                "from_total": from_total,
                "to_item": item.item_code,
                "to_qty": received_qty,
                "to_value": credit_value,
                "to_total": to_total,
                "qty_diff": qty_diff,
                "value_diff": value_diff,
                "indent": 1
            })

            total_issued_qty += qty
            total_received_qty += received_qty
            total_debit += from_total
            total_credit += to_total

    # Totals row
    data.append({
        "name": "TOTAL",
        "from_qty": total_issued_qty,
        "to_qty": total_received_qty,
        "from_total": total_debit,
        "to_total": total_credit,
        "indent": 0
    })

    return columns, data
