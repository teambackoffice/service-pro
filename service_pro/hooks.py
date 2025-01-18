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
after_migrate = ["service_pro.doc_events.after_migrate.execute"]

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
    "Sales Order" : "public/js/sales_order.js",
    "Purchase Receipt" : "public/js/purchase_receipt.js",
    "Material Request" : "public/js/material_request.js",
    "Delivery Note" : "public/js/delivery_note.js",
    "Additional Salary" : "public/js/additional_salary.js",
    "Landed Cost Voucher": "public/js/landed_cost_voucher.js",
    "Item": "public/js/item.js",
    "Employee": "public/js/employee.js",
    "Purchase Invoice" : "public/js/purchase_invoice.js",
    "Project" : "public/js/project.js",
    "Purchase Order" : "public/js/purchase_order.js",
    "Supplier Quotation" : "public/js/supplier_quotation.js",
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
        "before_submit":["service_pro.doc_events.sales_invoice.validate_so",
                         "service_pro.doc_events.sales_invoice.validate_permission",],
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
    "Sales Order": {
        "on_submit": [
            "service_pro.doc_events.sales_order.create_qr_code",
            "service_pro.doc_events.sales_order.sales_order_submit",
        ],
        "before_submit": "service_pro.doc_events.sales_order.validate_permission",

    },
    "Quotation":{
        "on_submit": "service_pro.doc_events.quotation.on_submit_quotation",
        "validate": "service_pro.doc_events.quotation.validate_item",
        "before_submit": "service_pro.doc_events.quotation.validate_permission",
    },
    "Purchase Receipt": {
        "before_submit": "service_pro.doc_events.purchase_receipt.update_supplier_packing_slip",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"service_pro.tasks.all"
	# ],
	"daily": [
		"service_pro.service_pro.doctype.service_order_form.service_order_form.check_service_order_expiry"
	],
	# "hourly": [
	# 	"service_pro.tasks.hourly"
	# ],
	# "weekly": [
	# 	"service_pro.tasks.weekly"
	# ]
	# "monthly": [
	# 	"service_pro.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "service_pro.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.doctype.event.event.get_events": "service_pro.event.get_events",
    "erpnext.stock.doctype.material_request.material_request.make_purchase_order": "service_pro.doc_events.material_request.make_purchase_order"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Stock Entry": "service_pro.doc_events.stock_entry_dashboard.get_stock_entry_data",
    "Purchase Order": "service_pro.doc_events.dashboard.dashboard.purchase_order_dashboard",
    "Purchase Receipt": "service_pro.doc_events.dashboard.dashboard.purchase_receipt",
    "Project": "service_pro.doc_events.dashboard.project_dashboard.project_dashboard",
    "Sales Order": "service_pro.doc_events.dashboard.dashboard.sales_order_dashboard",
   "Quotation": "service_pro.doc_events.dashboard.quotation_dashboard.quotation_dashboard",


}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "module",
                "in",
                "Service Pro"
            ]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "module",
                "in",
                "Service Pro"
            ]
        ]
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


