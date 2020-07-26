from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on transactions against this Estimation. See timeline below for details'),
		'fieldname': 'estimation',
		'transactions': [
			{
				'label': _('Production'),
				'items': ['Production']
			}
		]
	}