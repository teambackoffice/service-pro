from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'custom_inter_company_journal_entry',
		"non_standard_fieldnames": {
			"Journal Entry": "custom_inter_company_journal_entry"
			
		},
		'transactions': [
			{
				'label': _('Related'),'items': [ "Journal Entry"]
			}
		]
	}