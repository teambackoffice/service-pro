frappe.ui.form.on('Employee', {
    custom_gosi_basic_salary: calculate_vacation_salary,
    custom_gosi_other_allowance: calculate_vacation_salary,
    custom_gosi_housing_allowance: calculate_vacation_salary,

    refresh: calculate_vacation_salary
});

function calculate_vacation_salary(frm) {
    let basic_salary = frm.doc.custom_gosi_basic_salary || 0;
    let other_allowance = frm.doc.custom_gosi_other_allowance || 0;
    let housing_allowance = frm.doc.custom_gosi_housing_allowance || 0;

    let total_gosi_salary = basic_salary + other_allowance + housing_allowance;

    let vacation_salary = (total_gosi_salary / (12 * 30)) * 360;

    frm.set_value('custom_vacation_salary', vacation_salary);
}
