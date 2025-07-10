# Copyright (c) 2025, jan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
	compute_growth_view_data,
	compute_margin_view_data,
	get_columns,
	get_data,
	get_filtered_list_for_consolidated_report,
	get_period_list,
)


def get_all_companies(company):
	is_group = frappe.db.get_value("Company", company, "is_group")
	if not is_group:
		return [company]

	child_companies = frappe.get_all("Company", filters={"parent_company": company}, pluck="name")
	return [company] + child_companies


def execute(filters=None):
	companies = get_all_companies(filters.company)

	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	# Initialize merged income and expense
	merged_income = []
	merged_expense = []

	for comp in companies:
		# Ensure the correct company is passed in filters
		loop_filters = frappe._dict(filters.copy())
		loop_filters.company = comp

		income = get_data(
			comp,
			"Income",
			"Credit",
			period_list,
			filters=loop_filters,
			accumulated_values=loop_filters.accumulated_values,
			ignore_closing_entries=True,
		)
		expense = get_data(
			comp,
			"Expense",
			"Debit",
			period_list,
			filters=loop_filters,
			accumulated_values=loop_filters.accumulated_values,
			ignore_closing_entries=True,
		)

		merged_income = merge_financial_data(merged_income, income, period_list)
		merged_expense = merge_financial_data(merged_expense, expense, period_list)

	net_profit_loss = get_net_profit_loss(
		merged_income, merged_expense, period_list, filters.company, filters.presentation_currency
	)

	data = []
	data.extend(merged_income or [])
	data.extend(merged_expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)

	currency = filters.presentation_currency or frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)

	chart = get_chart_data(filters, columns, merged_income, merged_expense, net_profit_loss, currency)

	report_summary, primitive_summary = get_report_summary(
		period_list, filters.periodicity, merged_income, merged_expense, net_profit_loss, currency, filters
	)

	if filters.get("selected_view") == "Growth":
		compute_growth_view_data(data, period_list)

	if filters.get("selected_view") == "Margin":
		compute_margin_view_data(data, period_list, filters.accumulated_values)

	return columns, data, None, chart, report_summary, primitive_summary


def merge_financial_data(existing_data, new_data, period_list):
	if not existing_data:
		return new_data.copy()

	account_map = {d["account"]: d for d in existing_data if d.get("account")}

	for row in new_data:
		acc = row.get("account")
		if not acc:
			continue  # skip total or malformed rows

		if acc in account_map:
			existing_row = account_map[acc]
			for period in period_list:
				key = period.key
				existing_row[key] = flt(existing_row.get(key, 0)) + flt(row.get(key, 0))
		else:
			account_map[acc] = row

	return list(account_map.values())

def get_report_summary(
	period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

	# from consolidated financial statement
	if filters.get("accumulated_in_group_company"):
		period_list = get_filtered_list_for_consolidated_report(filters, period_list)

	if filters.accumulated_values:
		# when 'accumulated_values' is enabled, periods have running balance.
		# so, last period will have the net amount.
		key = period_list[-1].key
		if income:
			net_income = income[-2].get(key)
		if expense:
			net_expense = expense[-2].get(key)
		if net_profit_loss:
			net_profit = net_profit_loss.get(key)
	else:
		for period in period_list:
			key = period if consolidated else period.key
			if income:
				net_income += income[-2].get(key)
			if expense:
				net_expense += expense[-2].get(key)
			if net_profit_loss:
				net_profit += net_profit_loss.get(key)

	if len(period_list) == 1 and periodicity == "Yearly":
		profit_label = _("Profit This Year")
		income_label = _("Total Income This Year")
		expense_label = _("Total Expense This Year")
	else:
		profit_label = _("Net Profit")
		income_label = _("Total Income")
		expense_label = _("Total Expense")

	return [
		{"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "-"},
		{"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "=", "color": "blue"},
		{
			"value": net_profit,
			"indicator": "Green" if net_profit > 0 else "Red",
			"label": profit_label,
			"datatype": "Currency",
			"currency": currency,
		},
	], net_profit


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value = True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss


def get_chart_data(filters, columns, income, expense, net_profit_loss, currency):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({"name": _("Income"), "values": income_data})
	if expense_data:
		datasets.append({"name": _("Expense"), "values": expense_data})
	if net_profit:
		datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

	chart = {"data": {"labels": labels, "datasets": datasets}}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	chart["fieldtype"] = "Currency"
	chart["options"] = "currency"
	chart["currency"] = currency

	return chart
