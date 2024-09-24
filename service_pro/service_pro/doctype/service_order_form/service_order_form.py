# Copyright (c) 2024, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words, nowdate,getdate
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum


class ServiceOrderForm(Document):
    def validate(self):
        self.in_words = money_in_words(self.grand_total, self.currency)


def check_service_order_expiry():
    current_date = getdate(nowdate())
    service_orders = frappe.get_all('Service Order Form', filters={'status': 'Open','valid_till': ['<', current_date]},
        fields=['name', 'valid_till']
    )
    
    for order in service_orders:
        frappe.db.set_value('Service Order Form', order.name, 'status', 'Expired')
        frappe.db.commit() 

	


@frappe.whitelist()
def create_sales_order(source_name, target_doc=None):
    def update_sales_team(source, target):
        if source.sales_executive:
            if not target.sales_team:
                target.append('sales_team', {
                    'sales_person': source.sales_executive,                     
                })

    doclist = get_mapped_doc(
    "Service Order Form",
    source_name,
    {
        "Service Order Form": {
            "doctype": "Sales Order",
            "field_map": {
                "name": "custom_service_order_form_id", 
                "customer": "customer",
                "terms": "tc_name",
                "term_details": "terms",
                "vat_on": "taxes_and_charges", 
            }
        },
        "Service Order Form Item": {
            "doctype": "Sales Order Item",
            "field_map": {
            "item_description": "item_name",
            "qty": "qty",
            }
            }

    },
    target_doc,
    update_sales_team
    )

    return doclist








