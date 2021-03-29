import frappe
from erpnext.stock.utils import get_latest_stock_qty,get_stock_value_from_bin,get_stock_value_on,get_stock_balance

from frappe.utils import flt, cint, nowdate
def get_qty():
    # BLV - 0061
    print(get_stock_balance("BLV-0061", "Work In Progress - HYDROTECH"))


def update_purchase_receipt():
    purchase_receipt = frappe.db.sql(""" SELECT * FROM `tabPurchase Receipt` WHERE docstatus=1""",as_dict=1)
    for i in purchase_receipt:
        pr = frappe.get_doc("Purchase Receipt", i.name)

        for d in pr.items:
            if not d.cost_center:
                stock_value_diff = frappe.db.get_value("Stock Ledger Entry",
                                                       {"voucher_type": "Purchase Receipt", "voucher_no": i.name,
                                                        "voucher_detail_no": d.name, "warehouse": d.warehouse},
                                                       "stock_value_difference")
                if stock_value_diff:
                    valuation_amount_as_per_doc = flt(d.base_net_amount, d.precision("base_net_amount")) + \
                                                  flt(d.landed_cost_voucher_amount) + flt(d.rm_supp_cost) + flt(
                        d.item_tax_amount)

                    divisional_loss = flt(valuation_amount_as_per_doc - stock_value_diff,
                                          d.precision("base_net_amount"))


                    if divisional_loss:
                        frappe.db.sql(""" UPDATE `tabPurchase Receipt Item` SET cost_center='1003 - Site Service - HT' WHERE name=%s """, d.name)
                        frappe.db.commit()
                        print("DONE FOR ITEM " + d.name)