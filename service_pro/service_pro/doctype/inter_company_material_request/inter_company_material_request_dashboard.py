from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'inter_company_material_request',
		'transactions': [
			{
				'label': _('Related'),'items': [ "Inter Company Stock Transfer"]
			}
		]
	}