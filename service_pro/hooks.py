# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "service_pro"
app_title = "Service Pro"
app_publisher = "jan"
app_description = "Service Pro"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "janlloydangeles@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/service_pro/css/service_pro.css"
# app_include_js = "/assets/service_pro/js/service_pro.js"

# include js, css files in header of web template
# web_include_css = "/assets/service_pro/css/service_pro.css"
# web_include_js = "/assets/service_pro/js/service_pro.js"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Quotation" : "public/js/quotation.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Purchase Receipt" : "public/js/purchase_receipt.js",
    "Material Request" : "public/js/material_request.js",
    "Delivery Note" : "public/js/delivery_note.js",
    "Additional Salary" : "public/js/additional_salary.js",
    "Landed Cost Voucher": "public/js/landed_cost_voucher.js",
    "Item": "public/js/item.js",
    "Purchase Invoice" : "public/js/purchase_invoice.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "service_pro.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "service_pro.install.before_install"
# after_install = "service_pro.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "service_pro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"on_submit": "service_pro.doc_events.sales_invoice.on_submit_si",
        "before_submit":"service_pro.doc_events.sales_invoice.validate_so",
		"on_cancel": "service_pro.doc_events.sales_invoice.on_cancel_si",
	},
    #"File": {
		#"on_trash": "service_pro.doc_events.file.on_trash_f",
	#},
    "Delivery Note": {
		"on_submit": "service_pro.doc_events.delivery_note.change_status",
		"on_cancel": "service_pro.doc_events.delivery_note.change_status_cancel",
	},
    "Journal Entry": {
		"on_submit": "service_pro.doc_events.journal_entry.submit_jv",
        "on_cancel": "service_pro.doc_events.journal_entry.cancel_related_party_entry"
	},
    "Stock Ledger Entry":{
        "on_submit": "service_pro.doc_events.stock_ledger_entry.update_item_valuation_rate"
    },
    "Sales Order":{
        "on_submit": "service_pro.doc_events.sales_order.on_so_submit"
    },
    "Quotation":{
        "on_submit": "service_pro.doc_events.quotation.on_submit_quotation"
    },
    "Purchase Receipt":{
        "validate": "service_pro.doc_events.purchase_receipt.validate"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"service_pro.tasks.all"
# 	],
# 	"daily": [
# 		"service_pro.tasks.daily"
# 	],
# 	"hourly": [
# 		"service_pro.tasks.hourly"
# 	],
# 	"weekly": [
# 		"service_pro.tasks.weekly"
# 	]
# 	"monthly": [
# 		"service_pro.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "service_pro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "service_pro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "service_pro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Quotation-service_receipt_note",
                    "Sales Invoice-production",
                    "Journal Entry-production",
                    "Stock Entry-production",
                    "Delivery Note-production",
                    "Sales Invoice-amount_in_arabic_words_",
                    "Sales Invoice-paid",
                    "Sales Invoice Item-include_discount",
                    "Purchase Receipt-production",
                    "Material Request-production",
                    "Delivery Note-location",
                    "Delivery Note-sales_man_name",
                    "Delivery Note-sales_man",
                    "Sales Invoice-showroom_card",
                    "Sales Invoice-showroom_cash",
                    "Sales Invoice-cash",
                    "Sales Invoice-unpaid",
                    "Sales Invoice-liabilities_account",
                    "Sales Invoice-expense_account",
                    "Sales Invoice-expense_cost_center",
                    "Sales Invoice-incentive",
                    "Sales Invoice-incentive_journal",
                    "Sales Invoice-column_break_181",
                    "Sales Invoice-journal_entry",
                    "Sales Person-liabilities_account",
                    "Customer-sales_man",
                    "Customer-sales_man_name",
                    "Journal Entry-agent_payment_request",
                    "Quotation-site_visit_report",
                    "Journal Entry-petty_cash_request",
                    "Employee-petty_cash_account",
                    "Sales Invoice Item-si_discount",
                    "Material Request-site_visit_report",

                    "Salary Component-is_hour_based",
                    "Additional Salary-total_working_hour",
                    "Additional Salary-is_hour_based",


                    "Journal Entry-sales_invoice",
                    "Sales Invoice-agent_commision_record",
                    "Item-is_omfb_item",

                    "Journal Entry-related_party_entry",
                    "Journal Entry-is_related_party_entry_return",
                    "Landed Cost Item-avail_qty",
                    "Landed Cost Voucher-column_break_ahjhe",
                    "Landed Cost Voucher-column_break_62gb2",
                    "Landed Cost Voucher-refresh_avail_qty",
                    "Landed Cost Voucher-section_break_vraqz",

                    "Item-custom_size_specification",
                    "Item-custom_item_description",
                    "Item-custom_item_specification",
                    "Item-custom_brand_name",
                    "Item-custom_edit_valuation_rate",
                    "Item-custom_edit_naming_fields",

                    "Price List-custom_section_break_a0uow",
                    "Price List-custom_maximum_user_discount",
                    "Sales Order-custom_production",
                ]
            ]
        ]
    },
    {
        "dt":"Property Setter","filters":[["module","in",["Service Pro"]]]
    }
]

report_override_html = {
	"Accounts Receivable": "overrides/reports/html/accounts_receivable.html",
}
report_override = {
	"Accounts Receivable": "service_pro.overrides.reports.account_receivable.execute"
}
report_override_js = {
	"Accounts Receivable": "overrides/reports/js/accounts_receivable.js",
}

override_whitelisted_methods = {
	"frappe.desk.query_report.get_script": "service_pro.overrides.report.get_script",
}


