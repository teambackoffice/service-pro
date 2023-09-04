import frappe

def submit_jv(doc, method):
    if doc.agent_payment_request:
        frappe.db.sql(""" UPDATE `tabAgent Payment Request` SET agent_outstanding_amount=0, status='Paid' WHERE name=%s """, doc.agent_payment_request)
        frappe.db.commit()

    if doc.petty_cash_request:
        frappe.db.sql(""" UPDATE `tabPetty Cash Request` SET agent_outstanding_amount=0, status='Paid' WHERE name=%s """, doc.petty_cash_request)
        frappe.db.commit()

def cancel_related_party_entry(doc, method=None):
    if doc.related_party_entry and frappe.db.exists("Related Party Entry", doc.related_party_entry):
        #Find journal type and related payment entry
        rpe = frappe.get_doc("Related Party Entry", doc.related_party_entry)
        if doc.is_related_party_entry_return:
            rpe.returned_amount = rpe.returned_amount - doc.total_debit
            rpe.pending_amount = rpe.amount - rpe.returned_amount
            if rpe.pending_amount == rpe.amount:
                rpe.status = "Paid"
            elif rpe.pending_amount < rpe.amount:
                rpe.status = "Partially Returned"
            rpe.save(ignore_permissions=True)
        if not doc.is_related_party_entry_return:        
            je_list = frappe.db.get_list("Journal Entry", {"related_party_entry":rpe.name, "docstatus":1}, pluck="name")
            for je in je_list:
                frappe.get_doc("Journal Entry", je).cancel()
            rpe.reload()
            rpe.status = "Unpaid"
            rpe.returned_amount = 0.0
            rpe.pending_amount = 0.0
            rpe.save(ignore_permissions=True)
        # elif(rpe.type == "Debit To"):
        #     if doc.is_related_party_entry_return:
        #         rpe.returned_amount = rpe.returned_amount - doc.total_debit
        #         rpe.pending_amount = rpe.amount - rpe.returned_amount
        #         if rpe.pending_amount == rpe.amount:
        #             rpe.status = "Paid"
        #         elif rpe.pending_amount < rpe.amount:
        #             rpe.status = "Partially Returned"
        #         rpe.save(ignore_permissions=True)
        #     if not doc.is_related_party_entry_return:        
        #         je_list = frappe.db.get_list("Journal Entry", {"related_party_entry":rpe.name, "docstatus":1}, pluck="name")
        #         for je in je_list:
        #             frappe.get_doc("Journal Entry", je).cancel()
        #         rpe.reload()
        #         rpe.status = "Unpaid"
        #         rpe.returned_amount = 0.0
        #         rpe.pending_amount = 0.0
        #         rpe.save(ignore_permissions=True)