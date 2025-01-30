import frappe


def execute(filters=None):
    columns = [
        {"label": "Customer ID", "fieldname": "name", "fieldtype": "Data", "width": 200,"align":"center"},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200,"align":"center"},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 150,"length":1000,"align":"center"},
        {"label": "Customer Type", "fieldname": "customer_type", "fieldtype": "Data", "width": 200,"align":"center"},
        {"label": "Territory", "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 200,"align":"center"},
        {"label": "Mobile No", "fieldname": "phone", "fieldtype": "Data", "width": 200,"align":"center"},
        {"label": "Email", "fieldname": "email_id", "fieldtype": "Data", "width": 200,"align":"center"},
        {"label": "Customer Address ", "fieldname": "address_html", "fieldtype": "HTML", "width": 600,"align":"center"},
    ]

    # Fetching data from the database with additional fields from tabAddress
    data = frappe.db.sql("""
        SELECT 
            c.name, c.customer_name, c.customer_group, c.customer_type, c.territory,
            a.phone, a.email_id, a.address_title, a.address_type, a.address_line1, a.city, a.country
        FROM 
            tabCustomer c
        LEFT JOIN 
            tabAddress a ON a.idx = c.name
        LIMIT 5
    """, as_dict=True)

    # Process each row to generate the HTML address
    for row in data:
        if row.get("address_line1", "").strip():  # Check if the address is not empty or whitespace
            address_html = f"""
                {row.get('address_title', 'N/A')} -  {row.get('address_type', 'N/A')},  {row.get('address_line1', 'N/A')},  {row.get('city', 'N/A')}, {row.get('country', 'N/A')},  Email: {row.get('email_id', 'N/A')},  Phone: {row.get('phone', 'N/A')}<br>
               
            """
            row["address_html"] = address_html
        else:
            row["address_html"] = "<p>No Address Available</p>"

    return columns, data