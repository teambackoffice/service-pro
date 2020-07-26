from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on transactions against this Inspection. See timeline below for details'),
		'fieldname': 'inspection',
		'transactions': [
			{
				'label': _('Estimation'),
				'items': ['Estimation']
			}
		]
	}