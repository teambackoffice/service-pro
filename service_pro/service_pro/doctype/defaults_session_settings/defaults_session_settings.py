import frappe
from frappe.model.document import Document
from frappe import _
import json

class DefaultsSessionSettings(Document):
    pass

@frappe.whitelist()
def get_session_default_values(doctype_type=None):
    settings = frappe.get_doc("Defaults Session Settings")
    user_email = frappe.session.user

    for entry in settings.defaults:
        if entry.user == user_email and (doctype_type is None or entry.doctype_type == doctype_type):
            return {
                "company": entry.company,
                "cost_center": entry.cost_center,
                "set_warehouse": entry.set_warehouse
            }
    
    return {}