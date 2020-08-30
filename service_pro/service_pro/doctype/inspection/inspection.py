# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Inspection(Document):
	def on_submit(self):
		get_srn = frappe.db.sql(""" 
			     						SELECT * FROM `tabInspection` 
			     						WHERE service_receipt_note=%s and docstatus=1""", (self.service_receipt_note))
		if len(get_srn) > 0:
			self.check_status("To Estimation")

	def on_cancel(self):
		self.check_status("To Inspection")

	def check_status(self, status):
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s """,
					  (status,self.service_receipt_note))
		frappe.db.commit()

	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s """,(status, self.name))
		frappe.db.commit()