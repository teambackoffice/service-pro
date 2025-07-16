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
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100}
    ]

    data = []
    total_issued_qty = total_received_qty = total_debit = total_credit = 0

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

        # ---- Fetch all stock entries linked via Stock Entry Detail ----
        linked_se_details = frappe.get_all(
            "Stock Entry Detail",
            filters={"custom_inter_company_stock_transfer": transfer_id},
            fields=["parent", "item_code", "valuation_rate"],
            distinct=False
        )

        # Group entries by type
        debit_entry_id = credit_entry_id = material_issue_id = None
        debit_rate_map, credit_rate_map, material_issue_rate_map = {}, {}, {}

        for detail in linked_se_details:
            stock_entry = detail.parent
            entry_type = frappe.db.get_value("Stock Entry", stock_entry, "stock_entry_type")

            if entry_type == "Material Transfer":
                debit_entry_id = stock_entry
                debit_rate_map[detail.item_code] = detail.valuation_rate or 0
            elif entry_type == "Material Receipt":
                credit_entry_id = stock_entry
                credit_rate_map[detail.item_code] = detail.valuation_rate or 0
            elif entry_type == "Material Issue":
                material_issue_id = stock_entry
                material_issue_rate_map[detail.item_code] = detail.valuation_rate or 0

        # ---- Parent row (for report grouping) ----
        data.append({
            "name": transfer_id,
            "from_company": transfer.from_company,
            "to_company": transfer.to_company,
            "status": transfer.status,
            "posting_date": transfer.posting_date,
            "indent": 0
        })

        # ---- Line items ----
        items = frappe.get_all(
            "Inter Company Stock Transfer Item",
            filters={"parent": transfer_id},
            fields=["item_code", "qty", "received_qty"]
        )

        for item in items:
            item_code = item.item_code
            qty = item.qty or 0
            received_qty = item.received_qty or 0

            from_value = debit_rate_map.get(item_code, 0)
            to_value = credit_rate_map.get(item_code, 0)
            material_issue_rate = material_issue_rate_map.get(item_code, 0)

            from_total = qty * from_value
            to_total = received_qty * to_value
            qty_diff = qty - received_qty

            # ✅ Use Material Issue Rate in Value Diff
            value_diff = material_issue_rate

            data.append({
                "name": f"{transfer_id}-{item_code}",
                "parent_transfer": transfer_id,
                "from_item": item_code,
                "from_qty": qty,
                "from_value": from_value,
                "from_total": from_total,
                "debit_stock_entry": debit_entry_id,

                "to_item": item_code,
                "to_qty": received_qty,
                "to_value": to_value,
                "to_total": to_total,
                "credit_stock_entry": credit_entry_id,

                "qty_diff": qty_diff,
                "value_diff": value_diff,  # ← Material Issue rate
                "indent": 1
            })

            total_issued_qty += qty
            total_received_qty += received_qty
            total_debit += from_total
            total_credit += to_total

    # ---- Totals Row ----
    data.append({
        "name": "TOTAL",
        "from_qty": total_issued_qty,
        "to_qty": total_received_qty,
        "from_total": total_debit,
        "to_total": total_credit,
        "indent": 0
    })

    return columns, data
