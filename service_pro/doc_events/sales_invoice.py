import frappe

@frappe.whitelist()
def on_submit_si(doc, method):
    for prod in doc.production:
        production = frappe.db.sql(""" SELECT * FROM `tabProduction` WHERE name=%s """, prod.reference, as_dict=1)
        if len(production) > 0:
            if get_dn_si_qty("", production[0].qty, prod.reference)> 0:
                frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",("Partially Delivered", prod.reference))
                frappe.db.commit()
            else:
                frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",
                              ("Completed", prod.reference))
                frappe.db.commit()
@frappe.whitelist()
def on_cancel_si(doc, method):
    for prod in doc.production:
        frappe.db.sql(""" UPDATE `tabProduction` SET status=%s WHERE name=%s""",("In Progress", prod.reference))
        frappe.db.commit()


def get_dn_si_qty(item_code, qty, name):
	si_query = """ 
 			SELECT SII.qty as qty FROM `tabSales Invoice` AS SI 
 			INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name and SII.delivery_note is null
 			INNER JOIN `tabSales Invoice Production` AS SIP ON SI.name = SIP.parent 
 			WHERE SIP.reference=%s and SIP.parenttype=%s and SI.docstatus = 1
 			"""
	si = frappe.db.sql(si_query,(name,"Sales Invoice"), as_dict=1)
	dn_query = """ 
	 			SELECT DNI.qty as qty FROM `tabDelivery Note` AS DN 
	 			INNER JOIN `tabDelivery Note Item` AS DNI ON DNI.parent = DN.name
	 			INNER JOIN `tabSales Invoice Production` AS SIP ON DN.name = SIP.parent 
	 			WHERE SIP.reference=%s and SIP.parenttype=%s and DN.docstatus = 1
	 			"""
	dn = frappe.db.sql(dn_query,(name, "Delivery Note"), as_dict=1)

	total_qty = 0

	if len(si) > 0:
		for i in si:
			total_qty += i.qty

	if len(dn) > 0:
		for d in dn:
			total_qty += d.qty
	print(si)
	print(dn)
	print(float(qty) - float(total_qty))
	return float(qty) - float(total_qty)