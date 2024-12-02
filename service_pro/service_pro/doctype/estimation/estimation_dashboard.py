from __future__ import unicode_literals
from frappe import _

def get_data():
    return {
        'non_standard_fieldnames': {
            'Quotation': 'custom_estimation', 
        },
        'fieldname': 'custom_estimation',
        'transactions': [
            {
                'label': _('Quotation'),
                'items': ['Quotation']
            }
        ]
    }
