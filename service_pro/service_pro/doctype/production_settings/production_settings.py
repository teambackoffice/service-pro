# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProductionSettings(Document):
	@frappe.whitelist()
	def get_series(self):
		ps = frappe.db.sql(""" SELECT * FROM `tabProperty Setter` WHERE name='Item-naming_series-options'""", as_dict=1)
		naming_seriess = frappe.db.sql(
			""" SELECT fieldname, options FROM `tabDocField` WHERE parent='Item' AND fieldname='naming_series'; """)

		if len(ps) > 0:
			return ps[0].value
		if len(naming_seriess) > 0:
			return naming_seriess[0].options
