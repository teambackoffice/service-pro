from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'custom_inter_company_stock_transfer',
		'transactions': [
			{
				'label': _('Reference'),'items': [ "Stock Entry"]
			}
		]
	}