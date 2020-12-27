# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	print("laksdjlaksjdkalsjd")
	condition = ""
	condition_si = ""
	if filters.get("date"):
		condition += " and posting_date = '{0}'".format(filters.get("date"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		for i in filters.get("mop"):
			mop_array.append(i)
		condition_si = " INNER JOIN `tabSales Invoice Payment` AS SIP ON  SIP.parent = SI.name and SIP.mode_of_payment in {0}".format(tuple(mop_array))

	elif len(filters.get("mop")) == 1:
		condition_si = " INNER JOIN `tabSales Invoice Payment` AS SIP ON  SIP.parent = SI.name and SIP.mode_of_payment = '{0}'".format(filters.get("mop")[0])

	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "100"},
		{"label": "SI No", "fieldname": "name", "fieldtype": "Data","width": "150"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": "260"},
		{"label": "Sales Agent", "fieldname": "sales_man_agent", "fieldtype": "Data", "width": "120"},
		{"label": "Advance", "fieldname": "advance", "fieldtype": "Float", "precision": "2","width": "80"},
		{"label": "PE Received", "fieldname": "pe_received", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "JV Received", "fieldname": "jv_received", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "JV Paid (Dr)", "fieldname": "jv_paid", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "Agent Paid", "fieldname": "agent_paid", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "Agent Unpaid", "fieldname": "agent_unpaid", "fieldtype": "Float", "precision": "2", "width": "110"},
		{"label": "Net Amount", "fieldname": "net_amount", "fieldtype": "Float", "precision": "2", "width": "100"},
		{"label": "Status ", "fieldname": "status", "fieldtype": "Data", "options": "Sales Invoice", "width": "80"},
	]
	query = """ SELECT 
 					SI.*, 
 					(SELECT sales_person FROM `tabSales Team` AS ST WHERE ST.parent = SI.name LIMIT 1) as sales_man_agent 
 			  	FROM `tabSales Invoice` AS SI 
 			  	{0}
 			  	WHERE SI.docstatus=1 {1} 
 			  	ORDER BY customer_name ASC""".format(condition_si,condition)
	data = frappe.db.sql(query,as_dict=1)
	new_data = []
	for i in data:
		i['agent_paid' if i.paid and not i.unpaid else 'agent_unpaid' if not i.paid and i.unpaid else ""] = i.incentive
		i['net_amount'] = 0 - i.incentive if i.status == "Unpaid" and i.paid else i.grand_total - i.incentive if i.status == "Paid" and i.paid else i.grand_total if i.status == "Paid" and i.is_pos else 0
		i['status'] = i.status if i.status == "Paid" else ""
		new_data.append(i)

	pe_add(filters, new_data)
	jv_add(filters, new_data)
	jv_add_received(filters, new_data)
	jv_add_paid(filters, new_data)
	data_to_be_viewed = []
	if len(new_data) > 0:
		data_to_be_viewed = sorted(new_data, key=lambda x: x['customer_name'], reverse=True)
	return columns, data_to_be_viewed

def pe_add(filters, new_data):
	condition_pe = ""
	if filters.get("date"):
		condition_pe += " and PE.posting_date = '{0}'".format(filters.get("date"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		for i in filters.get("mop"):
			mop_array.append(i)
		condition_pe += " and PE.mode_of_payment in {0} ".format(tuple(mop_array))

	elif len(filters.get("mop")) == 1:
		condition_pe += " and PE.mode_of_payment = '{0}' ".format(filters.get("mop")[0])

	if len(filters.get("mop")) == 0:
		condition_pe += " and (PE.mode_of_payment = '{0}' or PE.mode_of_payment = '{1}')".format("Showroom Cash", "Showroom Card")

	payment_entry_query = """
					SELECT * FROM `tabPayment Entry`AS PE 
					WHERE PE.docstatus= 1 {0}""".format(condition_pe)
	pe = frappe.db.sql(payment_entry_query, as_dict=1)
	for iii in pe:
		# if iii.name not in list_of_pe:
		new_data.append({
			"posting_date": iii.posting_date,
			"customer_name": iii.party_name,
			"name": iii.name,
			"pe_received":iii.paid_amount,
			"net_amount":iii.paid_amount,
		})

def jv_add(filters, new_data):
	condition_jv = ""
	if filters.get("date"):
		condition_jv += " and JE.posting_date ='{0}' ".format(filters.get("date"))

	if len(filters.get("mop")) == 0:
		mop_name = " or JEI.account like '%Showroom Accrual - Card%' or JEI.account like '%Showroom Accrual - Cash%'"
		condition_jv += "and (JE.mode_of_payment in {0} {1})".format(('Showroom Cash', 'Showroom Card'), mop_name)

	if len(filters.get("mop")) > 1:
		mop_array = []
		mop_name = "or JEI.account like "
		for i in filters.get("mop"):
			mop_array.append(i)

		if "Showroom Cash" in mop_array:
			mop_name += "'%Showroom Accrual - Cash%'"

		if "Showroom Card" in mop_array:
			if "Showroom Accrual - Cash" in mop_name:
				mop_name += " or JEI.account like '%Showroom Accrual - Card%'"
			else:
				mop_name += " JEI.account like '%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment in {0} {1})".format(tuple(mop_array), mop_name)

	elif len(filters.get("mop")) == 1:
		mop_name = "JEI.account like "
		if filters.get("mop")[0] == "Showroom Cash":
			mop_name += "'%Showroom Accrual - Cash%'"

		if filters.get("mop")[0] == "Showroom Card":
			mop_name += "'%Showroom Accrual - Card%'"

		condition_jv += " and ({0})".format( mop_name)

	jv_query = """ 
    					SELECT JEI.parent, JEI.name, JE.posting_date, JEI.party, JEI.credit_in_account_currency FROM `tabJournal Entry`AS JE 
    					INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
    					WHERE JEI.is_advance = 'Yes' and JE.docstatus=1 {0} and JEI.credit_in_account_currency > 0""".format(condition_jv)
	print(jv_query)
	jv = frappe.db.sql(jv_query, as_dict=1)
	for ii in jv:
		new_data.append({
			"name": ii.parent,
			"posting_date": ii.posting_date,
			"customer_name": frappe.db.get_value("Customer", ii.party, "customer_name") if ii.party else "",
			"si_no": ii.parent,
			"advance": ii.credit_in_account_currency,
			"net_amount": ii.credit_in_account_currency,
		})

def jv_add_received(filters, new_data):
	condition_jv = ""
	if filters.get("date"):
		condition_jv += " and JE.posting_date ='{0}' ".format(filters.get("date"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		mop_name = "or JEI.account like "
		for i in filters.get("mop"):
			mop_array.append(i)

		if "Showroom Cash" in mop_array:
			mop_name += "'%Showroom Accrual - Cash%'"

		if "Showroom Card" in mop_array:
			if "Showroom Accrual - Cash" in mop_name:
				mop_name += " or JEI.account like '%Showroom Accrual - Card%'"
			else:
				mop_name += " JEI.account like '%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment in {0} {1})".format(tuple(mop_array), mop_name)

	elif len(filters.get("mop")) == 1:
		mop_name = "JEI.account like "
		if filters.get("mop")[0] == "Showroom Cash":
			mop_name += "'%Showroom Accrual - Cash%'"

		if filters.get("mop")[0] == "Showroom Card":
			mop_name += "'%Showroom Accrual - Card%'"

		condition_jv += " and ({1})".format(filters.get("mop")[0], mop_name)

	if len(filters.get("mop")) == 0:
		mop_name = " JEI.account like '%Showroom Accrual - Card%' or JEI.account like '%Showroom Accrual - Cash%'"
		condition_jv += "and ( {0})".format(mop_name)

	jv_query = """ 
    					SELECT JEI.parent, JEI.name, JE.posting_date, JEI.party, JEI.credit_in_account_currency, JEI.debit_in_account_currency FROM `tabJournal Entry`AS JE 
    					INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
    					WHERE JEI.is_advance = 'No' and JE.docstatus=1 {0}""".format(condition_jv)
	print(jv_query)
	jv = frappe.db.sql(jv_query, as_dict=1)
	for ii in jv:


		if ii.credit_in_account_currency > 0:
			new_data_object = {
				"name": ii.parent,
				"posting_date": ii.posting_date,
				"customer_name": frappe.db.get_value("Customer", ii.party, "customer_name") if ii.party else "",
				"si_no": ii.parent,
			}
			new_data_object['jv_received'] = ii.credit_in_account_currency
			new_data_object['net_amount'] = ii.credit_in_account_currency

			new_data.append(new_data_object)

def jv_add_paid(filters, new_data):
	condition_jv = ""
	if filters.get("date"):
		condition_jv += " and JE.posting_date ='{0}' ".format(filters.get("date"))

	if len(filters.get("mop")) > 1:
		mop_array = []
		mop_name = "or JEI.account like "
		for i in filters.get("mop"):
			mop_array.append(i)

		if "Showroom Cash" in mop_array:
			mop_name += "'%Showroom Accrual - Cash%'"

		if "Showroom Card" in mop_array:
			if "Showroom Accrual - Cash" in mop_name:
				mop_name += " or JEI.account like '%Showroom Accrual - Card%'"
			else:
				mop_name += " JEI.account like '%Showroom Accrual - Card%'"

		condition_jv += " and (JE.mode_of_payment in {0} {1})".format(tuple(mop_array), mop_name)

	elif len(filters.get("mop")) == 1:
		mop_name = "JEI.account like "
		if filters.get("mop")[0] == "Showroom Cash":
			mop_name += "'%Showroom Accrual - Cash%'"

		if filters.get("mop")[0] == "Showroom Card":
			mop_name += "'%Showroom Accrual - Card%'"

		condition_jv += " and ({1})".format(filters.get("mop")[0], mop_name)

	if len(filters.get("mop")) == 0:
		mop_name = " JEI.account like '%Showroom Accrual - Card%' or JEI.account like '%Showroom Accrual - Cash%'"
		condition_jv += "and ({0})".format(mop_name)

	jv_query = """ 
					SELECT 
						JEI.parent, 
						JEI.name, 
						JE.posting_date, 
						JEI.party, 
					  	JEI.credit_in_account_currency, 
					  	JEI.debit_in_account_currency
					FROM `tabJournal Entry`AS JE 
					INNER JOIN `tabJournal Entry Account` AS JEI ON JEI.parent = JE.name 
					WHERE JEI.is_advance = 'No' and JE.docstatus=1 {0} and JEI.party="" and JEI.debit_in_account_currency > 0""".format(condition_jv)
	print(jv_query)
	jv = frappe.db.sql(jv_query, as_dict=1)
	print("JV PAAAAAAAAAAAAAAAAAAAAID")
	for ii in jv:
		new_data_object = {
			"name": ii.parent,
			"posting_date": ii.posting_date,
			"customer_name": frappe.db.get_value("Customer", ii.party, "customer_name") if ii.party else "",
			"si_no": ii.parent,
		}

		new_data_object['jv_paid'] = ii.debit_in_account_currency
		new_data_object['net_amount'] = ii.debit_in_account_currency

		new_data.append(new_data_object)