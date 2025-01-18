from __future__ import unicode_literals
from frappe import _


def quotation_dashboard(data):
    return {
        'heatmap': True,
        'fieldname': 'custom_quotation',
        'transactions': [
            {
                'label': _('Sales Order'),
                'items': ['Sales Order']
            },
            {
                'label': _('Reference'),
                'items': ['Estimation']
            }
        ],
        "internal_links": {
            "Estimation": "custom_estimation"
        }
    }