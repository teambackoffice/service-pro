from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'heatmap': True,
        'heatmap_message': _('This is based on transactions against this Service Receipt Note. See timeline below for details'),
        'fieldname': 'custom_estimation',
        'transactions': [
            {
                'label': _('Quotation'),
                'items': ['Quotation']
            },
            {
                'label': _('Reference'),
                'items': ['Inspection']
            }
        ],
        "internal_links": {
            "Inspection": "inspection"
        }
    }