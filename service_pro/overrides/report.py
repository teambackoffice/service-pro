# Copyright (c) 2023, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.core.doctype.report.report import Report, get_report_module_dotted_path
from frappe.desk.query_report import get_report_doc
from frappe.model.utils import render_include
from frappe.modules import get_module_path, scrub
from frappe.utils import get_html_format


class CustomReport(Report):
	def execute_module(self, filters):
		# report in python module
		report_override = frappe.get_hooks("report_override", {})
		if report_override.get(self.name):
			method_name = report_override.get(self.name)[0]
		else:
			module = self.module or frappe.db.get_value("DocType", self.ref_doctype, "module")
			method_name = get_report_module_dotted_path(module, self.name) + ".execute"
		return frappe.get_attr(method_name)(frappe._dict(filters))


@frappe.whitelist()
def get_script(report_name):
	report = get_report_doc(report_name)
	module = report.module or frappe.db.get_value("DocType", report.ref_doctype, "module")

	is_custom_module = frappe.get_cached_value("Module Def", module, "custom")

	# custom modules are virtual modules those exists in DB but not in disk.
	module_path = "" if is_custom_module else get_module_path(module)
	report_folder = module_path and os.path.join(module_path, "report", scrub(report.name))

	report_override_js = frappe.get_hooks("report_override_js", {})
	if report_override_js.get(report_name):
		script_path = os.path.join(
			frappe.get_app_path("service_pro"), report_override_js.get(report_name)[0]
		)
	else:
		script_path = report_folder and os.path.join(
			report_folder, scrub(report.name) + ".js"
		)

	report_overide_html = frappe.get_hooks("report_override_html", {})
	if report_overide_html.get(report_name):
		print_path = os.path.join(
			frappe.get_app_path("service_pro"), report_overide_html.get(report_name)[0]
		)
	else:

		print_path = report_folder and os.path.join(
			report_folder, scrub(report.name) + ".html"
		)

	script = None
	if os.path.exists(script_path):
		with open(script_path) as f:
			script = f.read()
			script += f"\n\n//# sourceURL={scrub(report.name)}.js"

	html_format = get_html_format(print_path)

	if not script and report.javascript:
		script = report.javascript
		script += f"\n\n//# sourceURL={scrub(report.name)}__custom"

	if not script:
		script = "frappe.query_reports['%s']={}" % report_name

	return {
		"script": render_include(script),
		"html_format": html_format,
		"execution_time": frappe.cache().hget("report_execution_time", report_name) or 0,
	}
