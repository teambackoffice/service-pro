frappe.ui.form.on("Employee Rejoining", {
    employee_id: function(frm) {
        if (frm.doc.employee_id && frm.doc.date_of_departure && frm.doc.last_rejoining_date) {
            frm.trigger('recalculate');
        }
    },
    date_of_departure: function(frm) {
        frm.trigger('recalculate');
    },
    last_rejoining_date: function(frm) {
        frm.trigger('recalculate');
    },
    gosi_basic_salary: function(frm) {
        frm.trigger('recalculate');
    },
    travel_allowance: function(frm) {
        frm.trigger('recalculate');
    },
    bonus_allowance: function(frm) {
        frm.trigger('recalculate');
    },
    
    recalculate: function(frm) {
        if (!frm.is_new() && frm.is_dirty()) {
        }
    }
});