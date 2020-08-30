import frappe
#
# def change_status(doc, method):
#     for prod in doc.production:
#         production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
#         if len(production) > 0:
#             frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
#                           ("To Bill", prod.reference))
#             frappe.db.commit()


@frappe.whitelist()
def change_status(doc, method):
    for prod in doc.production:
        production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
        if len(production) > 0:
            print("GET LEEEEEEEEEEEEENGTHS")
            print(get_lengths(prod.reference))
            if get_dn_si_qty("", production[0].qty, prod.reference) == 0 and get_lengths(prod.reference)[0] == get_lengths(prod.reference)[1]:
                frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("Completed", prod.reference))
                frappe.db.commit()
                get_service_records(prod.reference)

            elif get_si_qty(prod.reference) >= 0 and \
                    ((get_dn_si_qty("", production[0].qty, prod.reference) >= 0 and  get_lengths(prod.reference)[0] !=
                             get_lengths(prod.reference)[1])) :
                frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Bill", prod.reference))
                frappe.db.commit()

            elif get_dn_si_qty("", production[0].qty, prod.reference) > 0:
                frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
                              ("Partially Delivered", prod.reference))
                frappe.db.commit()


def get_lengths(name):
    si_query = """ 
     			SELECT SIP.qty as qty FROM `tabSales Invoice` AS SI 
     			INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name and SII.delivery_note is null
     			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
     			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1
     			"""
    si = frappe.db.sql(si_query, (name, "Sales Invoice"), as_dict=1)
    dn_query = """ 
    	 			SELECT SIP.qty as qty FROM `tabDelivery Note` AS DN 
    	 			INNER JOIN `tabDelivery Note Item` AS DNI ON DNI.parent = DN.name
    	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
    	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1
    	 			"""
    dn = frappe.db.sql(dn_query, (name, "Delivery Note"), as_dict=1)

    return len(dn), len(si)
def get_service_records(reference):
    estimation_ = ""
    estimation = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name= %s""", reference, as_dict=1)
    if len(estimation) > 0:
        estimation_ = estimation[0].estimation
        frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s""",
					  ("Completed", estimation_))
    inspections = frappe.db.sql(""" SELECT * FROM `tabInspection Table` WHERE parent=%s """, estimation_, as_dict=1)
    for i in inspections:
        frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s""",
					  ("Completed", i.inspection))

    srn = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE name=%s """, estimation_, as_dict=1)
    if len(srn) > 0:
        srn_ = srn[0].receipt_note
        frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s""",
					 ("Completed", srn_))
    frappe.db.commit()

def change_status_cancel(doc, method):
    for prod in doc.production:
        frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""", ("To Deliver", prod.reference))
        frappe.db.commit()
        get_service_records_cancel(prod.reference)

def get_service_records_cancel(reference):
	estimation_ = ""
	estimation = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name= %s""", reference, as_dict=1)
	if len(estimation) > 0:
		estimation_ = estimation[0].estimation
		frappe.db.sql(""" UPDATE `tabEstimation` SET status=%s WHERE name=%s""",
					  ("To Production", estimation_))

	inspections = frappe.db.sql(""" SELECT * FROM `tabInspection Table` WHERE parent=%s """, estimation_, as_dict=1)
	for i in inspections:
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s""",
					  ("To Production", i.inspection))

	srn = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE name=%s """, estimation_, as_dict=1)
	if len(srn) > 0:
		srn_ = srn[0].receipt_note
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s""",
					  ("To Production", srn_))
	frappe.db.commit()

def get_si_qty(name):
    si_query = """ 
 			SELECT SIP.qty as qty FROM `tabSales Invoice` AS SI 
 			INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name
 			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
 			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1
 			"""
    si = frappe.db.sql(si_query, (name, "Sales Invoice"), as_dict=1)

    total_qty = 0

    if len(si) > 0:
        for i in si:
            total_qty += i.qty

    return float(total_qty)


def get_dn_si_qty(item_code, qty, name):
    si_query = """ 
 			SELECT SIP.qty as qty FROM `tabSales Invoice` AS SI 
 			INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name
 			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
 			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1
 			"""
    si = frappe.db.sql(si_query, (name, "Sales Invoice"), as_dict=1)
    dn_query = """ 
	 			SELECT SIP.qty as qty FROM `tabDelivery Note` AS DN 
	 			INNER JOIN `tabDelivery Note Item` AS DNI ON DNI.parent = DN.name
	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1
	 			"""
    dn = frappe.db.sql(dn_query, (name, "Delivery Note"), as_dict=1)

    total_qty = 0

    if len(si) > len(dn):
        for i in si:
            total_qty += i.qty

    elif len(dn) > len(si):
        for d in dn:
            total_qty += d.qty
    elif len(dn) == len(si):
        for d in dn:
            total_qty += d.qty
    return float(qty) - float(total_qty)

