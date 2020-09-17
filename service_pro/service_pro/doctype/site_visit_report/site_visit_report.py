# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SiteVisitReport(Document):
	def on_submit(self):
		for i in self.site_visit_report_jobs:
			if i.svrj_status == "Troubleshooting":
				doc_site_job = {
					"doctype": "Site Job Report",
					"customer": i.customer,
					"visit_time": i.visit_time,
					"contact_person": i.contact_person,
					"contact_number": i.contact_number,
					"site_visit_report": self.name
				}
				frappe.get_doc(doc_site_job).insert()