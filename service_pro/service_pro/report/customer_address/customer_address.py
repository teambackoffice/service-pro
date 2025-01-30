import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
   


def get_columns():
    columns=[
        _('Customer') + ':Link/Customer:150',
        _('Customer Name') + ':Data:150',      
        _('Address Line1') + ':Link/Address:150',
        _('Address Line2') + ':Link/Address:150',
        _('City') + ':Data:150',
        _('Postal code') + ':Data:150',
        _('Mobile No') + ':Data:150',
        _('Email Id') + ':Data:150',      
        _('Customer Type') + ':Data:150',
        _('Customer Group') + ':Link/Customer Group:150',
        _('Territory') + ':Link/Territory:150',      
             			
      ]
    return columns

def get_data(filters,customer=None):
    data = []   

    customers = frappe.get_all('Customer', fields=["name", "customer_name",  "territory", "customer_type", "customer_group", "mobile_no", "email_id","customer_primary_address","payment_terms","creation","owner","modified_by","customer_primary_contact"])
    
    for customer in customers:
        customer_data = {
            "customer": customer.name,
            "customer_name": customer.customer_name,
          
            "territory": customer.territory,
            "customer_type": customer.customer_type,
            "customer_group": customer.customer_group,
            "mobile_no": customer.mobile_no,
            "email_id": customer.email_id,
            
            "payment_terms": customer.payment_terms,
            "created_on": customer.creation,
            "changed_by":customer.modified_by,
            "created_by": customer.owner

        }

        address_line1 = frappe.get_value("Address", customer.customer_primary_address, "address_line1")
        # print(customer.customer_primary_address)
        if address_line1:
            customer_data["address_line1"]=address_line1
        address_line2= frappe.get_value("Address", customer.customer_primary_address,  "address_line2")
        if address_line2:
            customer_data["address_line2"]=address_line2
        city = frappe.get_value("Address", customer.customer_primary_address,  "city")
        if city:
            customer_data["city"]=city

        
        pincode=frappe.get_value("Address", customer.customer_primary_address,  "pincode")
        if pincode:
            customer_data["postal_code"]=pincode
       

        data.append(customer_data)
    
    return data