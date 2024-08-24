# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SiteVisitReport(Document):
	def validate(self):
		for i in self.site_visit_report_jobs:
			if i.rework and not i.job_card_number:
				frappe.throw(""" Job Card Number is required in row """ + str(i.idx))

	def on_submit(self):
		for i in self.site_visit_report_jobs:
			if i.svrj_status == "Troubleshooting" and not i.rework:
				# settings_value = frappe.get_single("Production Settings").__dict__
				data = frappe.db.sql(""" SELECT * FROM `tabSite Job Report Settings` WHERE company=%s """,self.company,as_dict=1)

				# print(settings_value)
				doc_site_job = {
					"doctype": "Site Job Report",
					"customer": i.customer,
					"visit_time": i.visit_time,
					"contact_person": i.contact_person,
					"contact_number": i.contact_number,
					"site_visit_report": self.name,
					"svrj_row_name": i.name,
					"rate_of_materials_based_on": data[0].rate_of_materials_based_on if len(data) > 0 else "",
					"price_list": data[0].price_list if len(data) > 0 else "",
				}
				site_job_name = frappe.get_doc(doc_site_job).insert()
				frappe.db.sql(""" UPDATE `tabSite Visit Report Jobs` SET job_card_number=%s WHERE name=%s""",
							  (site_job_name.name, i.name))
				frappe.db.commit()
			elif i.svrj_status == "Troubleshooting" and i.rework:
				frappe.db.sql(""" UPDATE `tabSite Job Report` SET site_visit_report=%s WHERE name=%s""",
							  (self.name, i.job_card_number))
				frappe.db.commit()
@frappe.whitelist()
def generate_sjr(name):
	get_job = frappe.db.sql(""" SELECT * FROM `tabSite Visit Report Jobs` WHERE name=%s""", name, as_dict=1)
	if len(get_job) > 0:
		data = frappe.db.sql(""" SELECT * FROM `tabSite Job Report Settings` WHERE company=%s """, self.company,
							 as_dict=1)

		# settings_value = frappe.get_single("Production Settings").__dict__

		doc_site_job = {
			"doctype": "Site Job Report",
			"customer": get_job[0].customer,
			"visit_time": get_job[0].visit_time,
			"contact_person": get_job[0].contact_person,
			"contact_number": get_job[0].contact_number,
			"site_visit_report": get_job[0].parent,
			"svrj_row_name": get_job[0].name,
			"rate_of_materials_based_on": data[0].rate_of_materials_based_on if len(data) > 0 else "",
					"price_list": data[0].price_list if len(data) > 0 else "",
		}
		site_job_name = frappe.get_doc(doc_site_job).insert()
		frappe.db.sql(""" UPDATE `tabSite Visit Report Jobs` SET job_card_number=%s WHERE name=%s""", (site_job_name.name,name))
		frappe.db.commit()