frappe.ui.form.on('Employee', {
    custom_gosi_basic_salary: calculate_vacation_salary,
    custom_gosi_other_allowance: calculate_vacation_salary,
    custom_gosi_housing_allowance: calculate_vacation_salary,
    
    refresh: function(frm) {
        calculate_vacation_salary(frm);
        
        if (!frm.is_new()) {
            frm.add_custom_button(__('Employee Rejoining'), function() {
                frappe.new_doc('Employee Rejoining', {
                    employee_id: frm.doc.name,
                    employee_name: frm.doc.employee_name,
                    designation: frm.doc.designation,
                    department: frm.doc.department,
                    company: frm.doc.company,
                    id_iqama_no: frm.doc.custom_iqama_number,
                    gosi_basic_salary: frm.doc.custom_vacation_salary,
                    expiry_date: frm.doc.custom_valid_uptos,
                    branch_region: frm.doc.branch
                });                
            }, __('Create'));
        }
    }
});


function calculate_vacation_salary(frm) {
    let basic_salary = frm.doc.custom_gosi_basic_salary || 0;
    let other_allowance = frm.doc.custom_gosi_other_allowance || 0;
    let housing_allowance = frm.doc.custom_gosi_housing_allowance || 0;

    let total_gosi_salary = basic_salary + other_allowance + housing_allowance;

    let vacation_salary = (total_gosi_salary / (12 * 30)) * 360;

    frm.set_value('custom_vacation_salary', vacation_salary);
}
