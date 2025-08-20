frappe.ui.form.on("Employee Rejoining", {
    refresh: function(frm) {
        calculate_all(frm);
    },
    gosi_basic_salary: function(frm) {
        calculate_all(frm);
    },
    number_of_working_days: function(frm) {
        calculate_all(frm);
    },
    travel_allowance: function(frm) {
        calculate_all(frm);
    },
    bonus_allowance: function(frm) {
        calculate_all(frm);
    },
    employee_id: function(frm) {
        calculate_all(frm);
    },
    date_of_departure: function(frm) {
        calculate_all(frm);
    },
    last_rejoining_date: function(frm) {
        calculate_all(frm);
    },
    validate: function(frm) {
        calculate_all(frm);
    }
});

function calculate_all(frm) {
    if (frm.doc.employee_id) {
        let filters = {
            employee: frm.doc.employee_id,
            leave_type: "Leave Without Pay",
            status: "Approved"
        };

        if (frm.doc.date_of_departure && frm.doc.last_rejoining_date) {
            filters["from_date"] = ["between", [frm.doc.date_of_departure, frm.doc.last_rejoining_date]];
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Leave Application",
                filters: filters,
                fields: ["total_leave_days"]
            },
            callback: function(r) {
                let total_days = 0;
                if (r.message) {
                    r.message.forEach(row => {
                        total_days += flt(row.total_leave_days);
                    });
                }
                frm.set_value("leave_application_count", total_days);

                let working_days = 0;
                if (frm.doc.count_vacation_days) {
                    working_days = frm.doc.count_vacation_days - total_days;
                    frm.set_value("number_of_working_days", working_days);
                }

                if (frm.doc.gosi_basic_salary && working_days) {
                    let base_salary = (frm.doc.gosi_basic_salary / 30 / 12) * working_days;
                    let travel = flt(frm.doc.travel_allowance);
                    let bonus = flt(frm.doc.bonus_allowance);
                    let total_salary = base_salary + travel + bonus;

                    frm.set_value("employee_vacation_salary", total_salary);
                }
            }
        });
    }
}
