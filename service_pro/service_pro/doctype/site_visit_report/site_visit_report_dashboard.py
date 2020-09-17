from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'site_visit_report',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ["Site Job Report"]
			}
		]
	}