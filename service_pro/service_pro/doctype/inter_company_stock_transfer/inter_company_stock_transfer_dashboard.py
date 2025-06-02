from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'custom_inter_company_stock_transfer',
		'internal_links': {
			'Inter Company Material Request': 'inter_company_material_request'
		},
		'transactions': [
			{
				'label': _('Reference'),
				'items': ['Stock Entry', "Inter Company Material Request"],
			}
		],
	}