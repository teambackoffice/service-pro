# Copyright (c) 2025, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class EmployeeRejoining(Document):
    
    def validate(self):
        if self.date_of_departure and self.last_rejoining_date:
            departure_date = getdate(self.date_of_departure)
            last_rejoining_date = getdate(self.last_rejoining_date)
            
   
            days_diff = (last_rejoining_date - departure_date).days
            self.count_vacation_days = days_diff
        else:
            self.count_vacation_days = 0