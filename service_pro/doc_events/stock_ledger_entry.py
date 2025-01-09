import frappe

def update_item_valuation_rate(doc, method=None):
        if doc.item_code :
            item_doc = frappe.get_doc("Item", {"item_code":doc.item_code})

            if doc.company == "HYDROTECH TRADING COMPANY-(D)":
                item_doc.custom_valuation_rate_htcd = doc.incoming_rate
            elif doc.company == "HYDROTECH COMPANY CENTRAL WAREHOUSE":
                item_doc.custom_valuation_rate_hccw = doc.incoming_rate
            elif doc.company == "HYDROTECH HYDRAULIC TRADING LLC":
                item_doc.custom_valuation_rate_hhtl = doc.incoming_rate
            elif doc.company == "HYDROTECH SERVICE COMPANY":
                item_doc.valuation_rate = doc.incoming_rate
            elif doc.company == "HYDROTECH TRADING COMPANY-(R)":
                item_doc.custom_valuation_rate_htcr = doc.incoming_rate
            elif doc.company == "HYDROTECH TRADING COMPANY-(J)":
                item_doc.custom_valuation_rate_htcj = doc.incoming_rate
            else:
                frappe.log_error(f"Unhandled company: {doc.company}", "Valuation Rate Update Error")

            item_doc.save(ignore_permissions=True)
