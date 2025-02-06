import frappe



@frappe.whitelist()
def get_salary_structure(employee, total_working_hours):
    ss = frappe.db.sql(""" SELECT * FROM `tabSalary Structure Assignment` WHERE employee=%s ORDER BY from_date DESC LIMIT 1""", (employee), as_dict=1)

    base = ss.base

    basic_salary = base/100*75
    house_rent_allowance = base/100*18.75

    gp = basic_salary + house_rent_allowance

    total = 0
    if len(ss) > 0:
        total = float((ss[0].gp / 30 / 8) * 1.5) * float(total_working_hours)
    return total