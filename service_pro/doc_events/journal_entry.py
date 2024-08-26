import frappe

def submit_jv(doc, method):
    if doc.agent_payment_request:
        frappe.db.sql(""" UPDATE `tabAgent Payment Request` SET agent_outstanding_amount=0, status='Paid' WHERE name=%s """, doc.agent_payment_request)
        frappe.db.commit()
        apr = frappe.get_doc("Agent Payment Request",doc.agent_payment_request)
        for x in apr.sales_invoice:
            spp = frappe.get_doc("Sales Partner Payments", x.sales_partner_payments)
            status = ""
            pa = 0
            if float(spp.incentive) == float(x.incentive):
                pa = spp.incentive
                status = "Paid"
            elif float(x.incentive) > 0:
                pa = spp.paid_amount + x.incentive
                status = "Partly Paid"

            balance = spp.incentive - pa
            frappe.db.sql(
                """ UPDATE `tabSales Partner Payments` SET balance_amount=%s,paid_amount=%s, status=%s WHERE name=%s """,
                (balance,pa,status,x.sales_partner_payments))
            frappe.db.commit()

    if doc.petty_cash_request:
        frappe.db.sql(""" UPDATE `tabPetty Cash Request` SET agent_outstanding_amount=0, status='Paid' WHERE name=%s """, doc.petty_cash_request)
        frappe.db.commit()

def cancel_related_party_entry(doc, method=None):
    if doc.sales_invoice:
        frappe.db.sql(""" UPDATE `tabSales Invoice` SET journal_entry='' WHERE name=%s """, doc.sales_invoice)
        frappe.db.commit()

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

    if doc.agent_payment_request:
        frappe.db.sql(""" UPDATE `tabAgent Payment Request` SET agent_outstanding_amount=claim_amount, status='Unpaid' WHERE name=%s """, doc.agent_payment_request)
        frappe.db.commit()
        apr = frappe.get_doc("Agent Payment Request",doc.agent_payment_request)
        for x in apr.sales_invoice:
            spp = frappe.get_doc("Sales Partner Payments", x.sales_partner_payments)
            status = ""
            balance = 0
            pa = spp.paid_amount - x.incentive
            if pa > 0:
                balance = spp.incentive - pa
                status = "Partly Paid"
            elif pa == 0:
                balance = spp.incentive
                status = "Unpaid"

            frappe.db.sql(
                """ UPDATE `tabSales Partner Payments` SET balance_amount=%s,paid_amount=%s, status=%s WHERE name=%s """,
                (balance,pa,status,x.sales_partner_payments))
            frappe.db.commit()