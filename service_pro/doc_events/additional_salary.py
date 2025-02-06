import frappe

@frappe.whitelist()
def get_salary_structure(employee, total_working_hours):
    ss = frappe.db.sql(
        """ SELECT * FROM `tabSalary Structure Assignment` WHERE employee=%s ORDER BY from_date DESC LIMIT 1""", 
        (employee,), 
        as_dict=True
    )

    salary_structure = ss[0]

    base = salary_structure.get("base", 0)

    basic_salary = base * 0.75
    house_rent_allowance = base * 0.1875

    gp = basic_salary + house_rent_allowance

    total = float((gp / 30 / 8) * 1.5) * float(total_working_hours)

    return total
