import frappe

@frappe.whitelist()
def get_production_settings_defaults(company):
    if company:
        defaults = {
            "item_naming_series": frappe.db.get_value("Production Settings", None, "item_naming_series") or "",
            "item_group": frappe.db.get_value("Production Settings", None, "item_group") or "",
            # "finish_good_cost_center": frappe.db.get_value("Production Settings", None, "finish_good_cost_center") or "",
            "credit_note_user_role": frappe.db.get_value("Production Settings", None, "credit_note_user_role") or "",
            "debit_note_user_role": frappe.db.get_value("Production Settings", None, "debit_note_user_role") or "",
            # "income_account": frappe.db.get_value("Production Settings", None, "income_account") or "",
            # "finish_good_warehouse": frappe.db.get_value("Production Settings", None, "finish_good_warehouse") or "",
            "mandatory_additional_cost_in_production": frappe.db.get_value("Production Settings", None, "mandatory_additional_cost_in_production") or 0,
            "enable_sales_order_validation": frappe.db.get_value("Production Settings", None, "enable_sales_order_validation") or 0,
            "automatically_create_jv": frappe.db.get_value("Production Settings", None, "automatically_create_jv") or 0,
        }
        tables = [
            "Raw Material Defaults",
            "Site Job Report Settings",
            "Inspection Settings",
            "Incentive Journal",
            "Sales Partner Payments Details",
            "Inter Company Stock Transfer From",
            "Inter Company Stock Transfer To",
            "Finish Good Defaults"
        ]
        for table in tables:
            data = frappe.db.sql(""" SELECT * FROM `tab{0}` WHERE company=%s """.format(table),company,as_dict=1)
            if len(data) > 0:
                defaults[data[0].parentfield] = data[0]

        return defaults