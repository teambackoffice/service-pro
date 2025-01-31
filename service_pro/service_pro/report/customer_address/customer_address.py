import frappe
from frappe import _

def execute(filters=None):
    # Fetch columns and data
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    # Define the columns for the report
    return [
        _('Customer') + ':Link/Customer:150',
        _('Customer Name') + ':Data:150',
        _('Address Line1') + ':Link/Address:150',
        _('Address Line2') + ':Link/Address:150',
        _('City') + ':Data:150',
        _('Postal code') + ':Data:150',
        _('Phone') + ':Data:150',  # Display name of the Phone column in the report
        _('email_id') + ':Data:150',
        _('Customer Type') + ':Data:150',
        _('Customer Group') + ':Link/Customer Group:150',
        _('Territory') + ':Link/Territory:150',
    ]

def get_data(filters, customer=None):
    data = []   

    # Fetch the customers along with the necessary fields
    customers = frappe.get_all('Customer', fields=["name", "customer_name", "territory", "customer_type", "customer_group",  "payment_terms", "creation", "owner", "modified_by",])
    
    for customer in customers:
        # Prepare customer data
        customer_data = {
            "customer": customer.name,
            "customer_name": customer.customer_name,
            "territory": customer.territory,
            "customer_type": customer.customer_type,
            "customer_group": customer.customer_group,
            "payment_terms": customer.payment_terms,
            "created_on": customer.creation,
            "changed_by": customer.modified_by,
            "created_by": customer.owner,
        }

        # Fetch the addresses linked to the customer using Dynamic Link
        dynamic_links = frappe.get_all('Dynamic Link', filters={'link_name': customer.name, 'link_doctype': 'Customer'}, fields=['parent'])

        for link in dynamic_links:
            # Fetch the address details for each linked address
            address = frappe.get_doc('Address', link.parent)
            if address:
                address_line1 = address.address_line1 if address.address_line1 else None
                address_line2 = address.address_line2 if address.address_line2 else None
                city = address.city if address.city else None
                pincode = address.pincode if address.pincode else None
                phone = address.phone if address.phone else None
                email = address.email_id if address.email_id else None

                # Update customer data with the address fields
                if address_line1:
                    customer_data["address_line1"] = address_line1
                if address_line2:
                    customer_data["address_line2"] = address_line2
                if city:
                    customer_data["city"] = city
                if pincode:
                    customer_data["postal_code"] = pincode
                if phone:
                    customer_data["phone"] = phone
                if email:
                    customer_data["email_id"] = email
        
        # Add the customer data to the list
        data.append(customer_data)
    
    return data
