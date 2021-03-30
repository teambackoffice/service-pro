import frappe



@frappe.whitelist()
def get_salary_structure(employee, total_working_hours):
    ss = frappe.db.sql(""" SELECT * FROM `tabSalary Structure Assignment` WHERE employee=%s ORDER BY from_date DESC LIMIT 1""", (employee), as_dict=1)

    total = 0
    if len(ss) > 0:
        total = float((ss[0].base / 30 / 8) * 1.5) * float(total_working_hours)
    return total