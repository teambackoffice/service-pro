from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'custom_service_order_form_id',
		
		'transactions': [
			{
				'label': _('Reference'),'items': [ "Sales Order"]
			}
		]
	}