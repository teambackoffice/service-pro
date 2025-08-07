import frappe
from frappe.utils import unique
from frappe.utils import today, nowdate, getdate, add_to_date
from frappe.utils import getdate, nowdate, get_year_start, get_year_ending

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
    
@frappe.whitelist()
def filter_purchase_order_status_count():
    po_count = frappe.db.count('Purchase Order', {
        'status': ['in', ['To Receive and Bill', 'To Receive']]
    })
    return po_count

@frappe.whitelist()
def filter_purchase_order_to_bill_status_count():
    po_count = frappe.db.count('Purchase Order', {
        'status': ['in', ['To Bill', 'To Receive and Bill']]
    })
    return po_count

@frappe.whitelist()
def filter_sales_order_status_count():
    so_count = frappe.db.count('Sales Order', {
        'status': ['in', ['To Deliver and Bill', 'To Deliver']]
    })
    return so_count

@frappe.whitelist()
def filter_sales_order_to_bill_status_count():
    so_count = frappe.db.count('Sales Order', {
        'status': ['in', ['To Deliver and Bill', 'To Bill']]
    })
    return so_count

@frappe.whitelist()
def filter_employee_active_status_count():
 
    employee_count = frappe.db.count('Employee', {
        'status': 'Active'
    })
    return employee_count

@frappe.whitelist()
def filter_employee_joined_this_year_count():

    from datetime import datetime
    
    current_year = datetime.now().year
    
    employee_count = frappe.db.count('Employee', {
        'date_of_joining': ['between', [f'{current_year}-01-01', f'{current_year}-12-31']]
    })
    return employee_count

@frappe.whitelist()
def filter_employee_exits_this_year_count():
 
    from datetime import datetime
    
    current_year = datetime.now().year
    
    employee_count = frappe.db.count('Employee', {
        'relieving_date': ['between', [f'{current_year}-01-01', f'{current_year}-12-31']]
    })
    return employee_count

@frappe.whitelist()
def get_annual_purchase_total():
    today = nowdate()
    start_date = get_year_start(today)
    end_date = get_year_ending(today)
    
    annual_purchase_total = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total_amount
        FROM `tabPurchase Invoice`
        WHERE creation BETWEEN %s AND %s
        AND status IN ('Paid', 'Overdue')
    """, (start_date, end_date), as_dict=True)
    
    total_amount = annual_purchase_total[0].total_amount if annual_purchase_total else 0
    
    # Get default currency
    default_currency = frappe.get_cached_value('Company', frappe.defaults.get_user_default('Company'), 'default_currency')
    if not default_currency:
        default_currency = 'SAR'
    
    # Format the amount
    if total_amount >= 1000000:
        formatted_amount = total_amount / 1000000
        amount_str = f"{formatted_amount:.2f} M".rstrip('0').rstrip('.')
        if amount_str.endswith(' M'):
            amount_str = amount_str.replace(' M', ' M')
    elif total_amount >= 1000:
        formatted_amount = total_amount / 1000
        amount_str = f"{formatted_amount:.2f} K".rstrip('0').rstrip('.')
        if amount_str.endswith(' K'):
            amount_str = amount_str.replace(' K', ' K')
    else:
        amount_str = f"{total_amount:.2f}"
    
    return f"{default_currency} {amount_str}"

@frappe.whitelist()
def get_annual_sales_total():
    today = nowdate()
    start_date = get_year_start(today)
    end_date = get_year_ending(today)
    
    annual_sales_total = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total_amount
        FROM `tabSales Invoice`
        WHERE creation BETWEEN %s AND %s
        AND status IN ('Paid', 'Overdue')
    """, (start_date, end_date), as_dict=True)
    
    total_amount = annual_sales_total[0].total_amount if annual_sales_total else 0
    
    # Get default currency
    default_currency = frappe.get_cached_value('Company', frappe.defaults.get_user_default('Company'), 'default_currency')
    if not default_currency:
        default_currency = 'SAR'
    
    # Format the amount
    if total_amount >= 1000000:
        formatted_amount = total_amount / 1000000
        amount_str = f"{formatted_amount:.2f} M".rstrip('0').rstrip('.')
        if amount_str.endswith(' M'):
            amount_str = amount_str.replace(' M', ' M')
    elif total_amount >= 1000:
        formatted_amount = total_amount / 1000
        amount_str = f"{formatted_amount:.2f} K".rstrip('0').rstrip('.')
        if amount_str.endswith(' K'):
            amount_str = amount_str.replace(' K', ' K')
    else:
        amount_str = f"{total_amount:.2f}"
    
    return f"{default_currency} {amount_str}"


@frappe.whitelist()
def get_all_time_sales_total():
    all_time_sales_total = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total_amount
        FROM `tabSales Invoice`
        WHERE status IN ('Paid', 'Overdue')
    """, as_dict=True)
    
    total_amount = all_time_sales_total[0].total_amount if all_time_sales_total else 0
    
    default_currency = frappe.get_cached_value('Company', frappe.defaults.get_user_default('Company'), 'default_currency')
    if not default_currency:
        default_currency = 'SAR'
    
    if total_amount >= 1000000:
        formatted_amount = total_amount / 1000000
        amount_str = f"{formatted_amount:.2f} M".rstrip('0').rstrip('.')
        if amount_str.endswith(' M'):
            amount_str = amount_str.replace(' M', ' M')
    elif total_amount >= 1000:
        formatted_amount = total_amount / 1000
        amount_str = f"{formatted_amount:.2f} K".rstrip('0').rstrip('.')
        if amount_str.endswith(' K'):
            amount_str = amount_str.replace(' K', ' K')
    else:
        amount_str = f"{total_amount:.2f}"
    
    return f"{default_currency} {amount_str}"

@frappe.whitelist()
def get_all_time_purchase_total():
    all_time_purchase_total = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total_amount
        FROM `tabPurchase Invoice`
        WHERE status IN ('Paid', 'Overdue')
    """, as_dict=True)
    
    total_amount = all_time_purchase_total[0].total_amount if all_time_purchase_total else 0
    
    default_currency = frappe.get_cached_value('Company', frappe.defaults.get_user_default('Company'), 'default_currency')
    if not default_currency:
        default_currency = 'SAR'
    
    if total_amount >= 1000000:
        formatted_amount = total_amount / 1000000
        amount_str = f"{formatted_amount:.2f} M".rstrip('0').rstrip('.')
        if amount_str.endswith(' M'):
            amount_str = amount_str.replace(' M', ' M')
    elif total_amount >= 1000:
        formatted_amount = total_amount / 1000
        amount_str = f"{formatted_amount:.2f} K".rstrip('0').rstrip('.')
        if amount_str.endswith(' K'):
            amount_str = amount_str.replace(' K', ' K')
    else:
        amount_str = f"{total_amount:.2f}"
    
    return f"{default_currency} {amount_str}"