# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Coalesce

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "label": _("Account"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Account",
            "width": 300
        },
        {
            "label": _("Account Name"),
            "fieldname": "account_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Account Type"),
            "fieldname": "account_type",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Root Type"),
            "fieldname": "root_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Credit Amount"),
            "fieldname": "credit_in_account_currency",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Debit Amount"),
            "fieldname": "debit_in_account_currency",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 150
        }
    ]

def get_data(filters):
    account_conditions = ["t0.account_type LIKE '%%Bank%%'", "t0.disabled = 0"]
    gl_conditions = ["t1.is_cancelled = 0", "t1.docstatus = 1"]
    
    # Add filters
    if filters:
        if filters.get("company"):
            account_conditions.append("t0.company = %(company)s")
            gl_conditions.append("t1.company = %(company)s")
        
        if filters.get("from_date"):
            gl_conditions.append("t1.posting_date >= %(from_date)s")
        
        if filters.get("to_date"):
            gl_conditions.append("t1.posting_date <= %(to_date)s")
        
        if filters.get("account"):
            account_conditions.append("t0.name = %(account)s")
        
        if not filters.get("include_opening"):
            gl_conditions.append("t1.is_opening = 0")
    
    query = """
        SELECT
            t5.name,
            t5.account_name,
            t5.account_type,
            t5.root_type,
            COALESCE(SUM(t4.credit_in_account_currency), 0) as total_credit,
            COALESCE(SUM(t4.debit_in_account_currency), 0) as total_debit,
            (COALESCE(SUM(t4.debit_in_account_currency), 0) - COALESCE(SUM(t4.credit_in_account_currency), 0)) as balance
        FROM (
            SELECT
                t0.name,
                t0.account_name,
                t0.account_type,
                t0.root_type
            FROM `tabAccount` AS t0
            WHERE {account_where}
        ) AS t5
        LEFT OUTER JOIN (
            SELECT
                t1.account,
                t1.credit_in_account_currency,
                t1.debit_in_account_currency,
                t1.is_cancelled
            FROM `tabGL Entry` AS t1
            WHERE {gl_where}
        ) AS t4 ON t5.name = t4.account
        GROUP BY t5.name, t5.account_name, t5.account_type, t5.root_type
        ORDER BY t5.account_name
    """.format(
        account_where=' AND '.join(account_conditions),
        gl_where=' AND '.join(gl_conditions)
    )
    
    data = frappe.db.sql(query, filters or {}, as_dict=1)
    
    for row in data:
        row["credit_in_account_currency"] = row.get("total_credit", 0)
        row["debit_in_account_currency"] = row.get("total_debit", 0)
        row["balance"] = row.get("balance", 0)
    
    return data

def get_data_orm_method(filters):
    
    Account = DocType('Account')
    GLEntry = DocType('GL Entry')
    
    bank_accounts_query = (
        frappe.qb.from_(Account)
        .select(
            Account.name,
            Account.account_name,
            Account.account_type,
            Account.root_type
        )
        .where(
            (Account.account_type.like('%Bank%')) &
            (Account.disabled == 0)
        )
    )
    
    if filters and filters.get("company"):
        bank_accounts_query = bank_accounts_query.where(Account.company == filters.get("company"))
    
    bank_accounts = bank_accounts_query.run(as_dict=True)
    
    result_data = []
    
    for account in bank_accounts:
        gl_query = (
            frappe.qb.from_(GLEntry)
            .select(
                Coalesce(Sum(GLEntry.credit_in_account_currency), 0).as_("total_credit"),
                Coalesce(Sum(GLEntry.debit_in_account_currency), 0).as_("total_debit")
            )
            .where(
                (GLEntry.account == account.name) &
                (GLEntry.is_cancelled == 0) &
                (GLEntry.docstatus == 1)
            )
        )
        
        if filters:
            if filters.get("from_date"):
                gl_query = gl_query.where(GLEntry.posting_date >= filters.get("from_date"))
            if filters.get("to_date"):
                gl_query = gl_query.where(GLEntry.posting_date <= filters.get("to_date"))
            if not filters.get("include_opening"):
                gl_query = gl_query.where(GLEntry.is_opening == 0)
        
        gl_data = gl_query.run(as_dict=True)
        
        if gl_data:
            total_credit = gl_data[0].get("total_credit", 0)
            total_debit = gl_data[0].get("total_debit", 0)
            balance = total_debit - total_credit
            
            result_data.append({
                "name": account.name,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "root_type": account.root_type,
                "credit_in_account_currency": total_credit,
                "debit_in_account_currency": total_debit,
                "balance": balance
            })
        else:
            result_data.append({
                "name": account.name,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "root_type": account.root_type,
                "credit_in_account_currency": 0,
                "debit_in_account_currency": 0,
                "balance": 0
            })
    
    return result_data