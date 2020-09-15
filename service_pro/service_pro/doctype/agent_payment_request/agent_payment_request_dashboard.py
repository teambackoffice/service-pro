from frappe import _


def get_data():
	return {
		'fieldname': 'agent_payment_request',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ["Journal Entry"]
			}
		]
	}