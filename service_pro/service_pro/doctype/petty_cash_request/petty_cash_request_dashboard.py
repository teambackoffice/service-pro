from frappe import _


def get_data():
	return {
		'fieldname': 'petty_cash_request',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ["Journal Entry"]
			}
		]
	}