from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'site_job_report',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ['Production']
			}
		]
	}