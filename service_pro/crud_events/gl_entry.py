# Copyright (c) 2023, Wahni IT Solutions and contributors
# For license information, please see license.txt

import frappe


def apply_gl_coding(doc, method=None):
	gl_coding_settings = frappe.get_cached_doc("GL Coding Settings")
	if not gl_coding_settings.enabled:
		return

	gl_code = []
	for row in gl_coding_settings.coding:
		if docname := doc.get(row.gl_field):
			code = frappe.db.get_value(row.linked_doctype, docname, row.code_field, cache=True)
			if not code:
				code = row.default_value
			gl_code.append(code)
		else:
			gl_code.append(row.default_value)

	if gl_coding_settings.trailing_code:
		gl_code.append(gl_coding_settings.trailing_code)

	doc.gl_code = f"{gl_coding_settings.gl_code_separator}".join(gl_code)
