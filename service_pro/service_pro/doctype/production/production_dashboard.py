from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'production',
		'non_standard_fieldnames': {
			'Sales Invoice': 'reference',
			'Delivery Note': 'reference',
			'Stock Entry': 'production',
		},
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ['Sales Invoice', "Delivery Note", "Stock Entry", "Job Completion Report"]
			}
		]
	}