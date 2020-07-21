# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Estimation(Document):
	pass

@frappe.whitelist()
def get_dimensions():
	rod_dia, r_length, tube_size, t_length = [],[],[],[]

	dimensions = frappe.get_single("Cylinder Dimensions").__dict__

	for rod in dimensions['rod_dia']:
		rod_dia.append(rod.dimension)

	for r in dimensions['r_length']:
		r_length.append(r.dimension)

	for tube in dimensions['tube_size']:
		tube_size.append(tube.dimension)

	for t in dimensions['t_length']:
		t_length.append(t.dimension)

	return rod_dia, r_length, tube_size, t_length