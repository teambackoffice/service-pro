from __future__ import unicode_literals
from frappe import _

def get_data():
    return {
        'heatmap': True,
        'heatmap_message': _('This is based on transactions against this Service Receipt Note. See timeline below for details'),
        'fieldname': 'service_receipt_note',
        'transactions': [
            {
                'label': _('Inspection'),
                'items': ['Inspection']
            },
            {
                'label': _('Reference'),
                'items': ['Project']
            }
        ],
        "internal_links": {
            "Project": "project"
        }
    }
