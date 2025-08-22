# Copyright (c) 2025, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, flt

class EmployeeRejoining(Document):
    
    def validate(self):
        self.calculate_vacation_days()
        self.calculate_leave_days()
        self.calculate_salary()
    
    def calculate_vacation_days(self):
        if self.date_of_departure and self.last_rejoining_date:
            departure_date = getdate(self.date_of_departure)
            last_rejoining_date = getdate(self.last_rejoining_date)
            
            days_diff = (last_rejoining_date - departure_date).days
            self.count_vacation_days = days_diff
        else:
            self.count_vacation_days = 0
    
    def calculate_leave_days(self):
        if not self.employee_id:
            self.leave_application_count = 0
            return
            
        filters = {
            'employee': self.employee_id,
            'leave_type': 'Leave Without Pay',
            'status': 'Approved'
        }
        
        if self.date_of_departure and self.last_rejoining_date:
            filters['from_date'] = ['between', [self.date_of_departure, self.last_rejoining_date]]
        
        try:
            leave_applications = frappe.get_list(
                'Leave Application',
                filters=filters,
                fields=['total_leave_days']
            )
            
            total_leave_days = sum(flt(app.total_leave_days) for app in leave_applications)
            self.leave_application_count = total_leave_days
        except Exception as e:
            frappe.log_error(f"Error calculating leave days: {str(e)}", "Employee Rejoining")
            self.leave_application_count = 0
    
    def calculate_salary(self):
        if not (self.gosi_basic_salary and self.count_vacation_days):
            self.employee_vacation_salary = 0
            self.number_of_working_days = 0
            return
            
        leave_days = flt(self.leave_application_count)
        working_days = max(0, flt(self.count_vacation_days) - leave_days)
        self.number_of_working_days = working_days
        
        if working_days > 0:
            base_salary = (flt(self.gosi_basic_salary) / 30 / 12) * working_days
            
            travel_allowance = flt(self.travel_allowance)
            bonus_allowance = flt(self.bonus_allowance)
            
            total_salary = base_salary + travel_allowance + bonus_allowance
            self.employee_vacation_salary = total_salary
        else:
            self.employee_vacation_salary = 0