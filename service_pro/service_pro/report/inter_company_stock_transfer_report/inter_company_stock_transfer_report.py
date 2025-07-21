import frappe

def execute(filters=None):
    columns = [
        {"label": "ID", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "From Company", "fieldname": "from_company", "fieldtype": "Data", "width": 200},
        {"label": "From Item", "fieldname": "from_item", "fieldtype": "Data", "width": 120},
        {"label": "Issued Qty", "fieldname": "from_qty", "fieldtype": "Float", "width": 100},
        {"label": "Debit Rate", "fieldname": "from_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total Debit", "fieldname": "from_total", "fieldtype": "Currency", "width": 100},
        {"label": "Debit Stock Entry", "fieldname": "debit_stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 150},

        {"label": "To Company", "fieldname": "to_company", "fieldtype": "Data", "width": 200},
        {"label": "To Item", "fieldname": "to_item", "fieldtype": "Data", "width": 120},
        {"label": "Received Qty", "fieldname": "to_qty", "fieldtype": "Float", "width": 100},
        {"label": "Credit Rate", "fieldname": "to_value", "fieldtype": "Currency", "width": 100},
        {"label": "Total Credit", "fieldname": "to_total", "fieldtype": "Currency", "width": 100},
        {"label": "Credit Stock Entry", "fieldname": "credit_stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 150},

        {"label": "Qty Diff", "fieldname": "qty_diff", "fieldtype": "Float", "width": 80},
        {"label": "Value Diff (Material Issue)", "fieldname": "value_diff", "fieldtype": "Currency", "width": 100},
        {"label": "Total Diff Value", "fieldname": "total_diff_value", "fieldtype": "Currency", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100}
    ]

    data = []

    # Filter setup
    transfer_filters = {
        key: val for key, val in (filters or {}).items()
        if key in ["from_company", "to_company", "status", "name", "posting_date"]
    }

    if filters and filters.get("from_date") and filters.get("to_date"):
        transfer_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]

    transfers = frappe.get_all(
        "Inter Company Stock Transfer",
        filters=transfer_filters,
        fields=["name", "from_company", "to_company", "status", "posting_date"]
    )

    for transfer in transfers:
        transfer_id = transfer.name

        # Initialize totals
        issued_qty = received_qty = debit_total = credit_total = 0
        debit_rate_total = credit_rate_total = value_diff_total = total_diff_value_total = 0

        # Fetch rate maps
        debit_rate_map, credit_rate_map, material_issue_rate_map = {}, {}, {}
        debit_entry_id = credit_entry_id = material_issue_id = None

        linked_se_details = frappe.get_all(
            "Stock Entry Detail",
            filters={"custom_inter_company_stock_transfer": transfer_id},
            fields=["parent", "item_code", "valuation_rate"]
        )

        for detail in linked_se_details:
            entry_type = frappe.db.get_value("Stock Entry", detail.parent, "stock_entry_type")
            if entry_type == "Material Transfer":
                debit_entry_id = detail.parent
                debit_rate_map[detail.item_code] = detail.valuation_rate or 0
            elif entry_type == "Material Receipt":
                credit_entry_id = detail.parent
                credit_rate_map[detail.item_code] = detail.valuation_rate or 0
            elif entry_type == "Material Issue":
                material_issue_id = detail.parent
                material_issue_rate_map[detail.item_code] = detail.valuation_rate or 0

        # Get all items under this transfer
        items = frappe.get_all(
            "Inter Company Stock Transfer Item",
            filters={"parent": transfer_id},
            fields=["item_code", "qty", "received_qty"]
        )

        # Prepare child rows
        child_rows = []

        for item in items:
            item_code = item.item_code
            qty = item.qty or 0
            rec_qty = item.received_qty or 0

            from_value = debit_rate_map.get(item_code, 0)
            to_value = credit_rate_map.get(item_code, 0)
            material_issue_rate = material_issue_rate_map.get(item_code, 0)

            from_total = qty * from_value
            to_total = rec_qty * to_value
            qty_diff = qty - rec_qty
            value_diff = to_value - from_value
            total_diff_value = to_total - from_total

            child_rows.append({
                "name": f"{transfer_id}-{item_code}",
                "from_item": item_code,
                "from_qty": qty,
                "from_value": from_value,
                "from_total": from_total,
                "debit_stock_entry": debit_entry_id,
                "to_item": item_code,
                "to_qty": rec_qty,
                "to_value": to_value,
                "to_total": to_total,
                "credit_stock_entry": credit_entry_id,
                "qty_diff": qty_diff,
                "value_diff": value_diff,
                "total_diff_value": total_diff_value,
                "indent": 1
            })

            # Totals for parent
            issued_qty += qty
            received_qty += rec_qty
            debit_total += from_total
            credit_total += to_total
            debit_rate_total += from_value
            credit_rate_total += to_value
            value_diff_total += value_diff
            total_diff_value_total += total_diff_value

        # Parent row with totals
        data.append({
            "name": transfer_id,
            "from_company": transfer.from_company,
            "to_company": transfer.to_company,
            "from_qty": issued_qty,
            "to_qty": received_qty,
            "from_value": debit_rate_total,
            "to_value": credit_rate_total,
            "from_total": debit_total,
            "to_total": credit_total,
            "value_diff": value_diff_total,
            "total_diff_value": total_diff_value_total,
            "status": transfer.status,
            "posting_date": transfer.posting_date,
            "indent": 0
        })

        # Add all item rows after parent
        data.extend(child_rows)

    return columns, data
