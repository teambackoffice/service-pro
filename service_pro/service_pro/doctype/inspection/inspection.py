# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from PIL import Image
import os
from os.path import dirname


class Inspection(Document):
	def on_submit(self):
		get_srn = frappe.db.sql(""" 
			     						SELECT * FROM `tabInspection` 
			     						WHERE service_receipt_note=%s and docstatus=1""", (self.service_receipt_note))
		if len(get_srn) > 0:
			self.check_status("To Estimation")

	def on_cancel(self):
		self.check_status("To Inspection")

	@frappe.whitelist()
	def check_status(self, status):
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s """,
					  (status,self.service_receipt_note))
		frappe.db.commit()

	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabInspection` SET status=%s WHERE name=%s """,(status, self.name))
		frappe.db.commit()

	def validate(self):
		self.crop_images()

	@frappe.whitelist()
	def crop_images(self):
		settings = frappe.get_single("Production Settings").__dict__
		for i in range(1,41):
			if eval("self.attach_" + str(i)):
				if 'private' not in eval("self.attach_" + str(i)):
					im = Image.open(frappe.get_site_path() + "/public" + eval("self.attach_" + str(i)))
				else:
					im = Image.open(frappe.get_site_path() + eval("self.attach_" + str(i)))

				width, height = im.size
				if width > settings['image_width'] and height > settings['image_height']:
					width = settings['image_width']
					height = settings['image_height']
					area = im.resize((width, height))
					area.save(frappe.get_site_path() + "/public" + eval("self.attach_" + str(i)), quality=95)
