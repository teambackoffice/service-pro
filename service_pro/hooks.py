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
		"on_cancel": "service_pro.doc_events.sales_invoice.on_cancel_si",
	},
    "File": {
		"on_trash": "service_pro.doc_events.file.on_trash_f",
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
                    "Sales Invoice-sales_man",
                    "Sales Invoice-sales_man_name",
                    "Sales Invoice-paid",
                    "Sales Invoice Item-include_discount",
                    "Purchase Receipt-production",
                    "Material Request-production"
                ]
            ]
        ]
    }
]


