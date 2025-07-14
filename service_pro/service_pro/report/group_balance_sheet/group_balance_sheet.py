import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.accounts.report.financial_statements import (
	get_columns,
	get_data,
	get_period_list,
	compute_growth_view_data,
)

def execute(filters=None):
	if not filters:
		filters = {}

	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	filters.period_start_date = period_list[0]["year_start_date"]

	currency = filters.presentation_currency or frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)

	# Get companies to include
	companies = [filters.company]
	if filters.get("accumulated_in_group_company"):
		child_companies = frappe.get_all("Company", filters={"parent_company": filters.company}, pluck="name")
		companies.extend(child_companies)

	# Merge data from all companies
	asset, liability, equity = [], [], []

	for company in companies:
		# Set company in filters
		filters.company = company

		asset += get_data(
			company, "Asset", "Debit", period_list,
			only_current_fiscal_year=False, filters=filters,
			accumulated_values=filters.accumulated_values
		) or []

		liability += get_data(
			company, "Liability", "Credit", period_list,
			only_current_fiscal_year=False, filters=filters,
			accumulated_values=filters.accumulated_values
		) or []

		equity += get_data(
			company, "Equity", "Credit", period_list,
			only_current_fiscal_year=False, filters=filters,
			accumulated_values=filters.accumulated_values
		) or []

	provisional_profit_loss, total_credit = get_provisional_profit_loss(
		asset, liability, equity, period_list, filters.company, currency
	)

	message, opening_balance = check_opening_balance(asset, liability, equity)

	data = asset + liability + equity

	if opening_balance and round(opening_balance, 2) != 0:
		unclosed = {
			"account_name": "'" + _("Unclosed Fiscal Years Profit / Loss (Credit)") + "'",
			"account": "'" + _("Unclosed Fiscal Years Profit / Loss (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency,
		}
		for period in period_list:
			unclosed[period.key] = opening_balance
			if provisional_profit_loss:
				provisional_profit_loss[period.key] -= opening_balance

		unclosed["total"] = opening_balance
		data.append(unclosed)

	if provisional_profit_loss:
		data.append(provisional_profit_loss)
	if total_credit:
		data.append(total_credit)

	columns = get_columns(
		filters.periodicity, period_list,
		filters.accumulated_values, company=filters.company
	)

	chart = get_chart_data(filters, columns, asset, liability, equity, currency)

	report_summary, primitive_summary = get_report_summary(
		period_list, asset, liability, equity, provisional_profit_loss, currency, filters
	)

	if filters.get("selected_view") == "Growth":
		compute_growth_view_data(data, period_list)

	return columns, data, message, chart, report_summary, primitive_summary


def get_provisional_profit_loss(asset, liability, equity, period_list, company, currency=None):
	provisional_profit_loss = {}
	total_row = {}

	if asset:
		total = total_row_total = 0
		currency = currency or frappe.get_cached_value("Company", company, "default_currency")
		total_row = {
			"account_name": "'" + _("Total (Credit)") + "'",
			"account": "'" + _("Total (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency,
		}
		has_value = False

		for period in period_list:
			key = period.key
			total_assets = flt(asset[-2].get(key))
			effective_liability = 0.0

			if liability and liability[-1] == {}:
				effective_liability += flt(liability[-2].get(key))
			if equity and equity[-1] == {}:
				effective_liability += flt(equity[-2].get(key))

			provisional_profit_loss[key] = total_assets - effective_liability
			total_row[key] = provisional_profit_loss[key] + effective_liability

			if provisional_profit_loss[key]:
				has_value = True

			total += flt(provisional_profit_loss[key])
			total_row_total += flt(total_row[key])

		provisional_profit_loss["total"] = total
		total_row["total"] = total_row_total

		if has_value:
			provisional_profit_loss.update({
				"account_name": "'" + _("Provisional Profit / Loss (Credit)") + "'",
				"account": "'" + _("Provisional Profit / Loss (Credit)") + "'",
				"warn_if_negative": True,
				"currency": currency,
			})

	return provisional_profit_loss, total_row


def check_opening_balance(asset, liability, equity):
	opening_balance = 0
	float_precision = cint(frappe.db.get_default("float_precision")) or 2

	if asset:
		opening_balance += flt(asset[-1].get("opening_balance", 0), float_precision)
	if liability:
		opening_balance -= flt(liability[-1].get("opening_balance", 0), float_precision)
	if equity:
		opening_balance -= flt(equity[-1].get("opening_balance", 0), float_precision)

	opening_balance = flt(opening_balance, float_precision)
	if opening_balance:
		return _("Previous Financial Year is not closed"), opening_balance
	return None, None


def get_report_summary(period_list, asset, liability, equity, provisional_profit_loss, currency, filters):
	net_asset = net_liability = net_equity = net_provisional_profit_loss = 0.0

	if filters.get("accumulated_values"):
		period_list = [period_list[-1]]

	for period in period_list:
		key = period.key
		if asset:
			net_asset += asset[-2].get(key)
		if liability and liability[-1] == {}:
			net_liability += liability[-2].get(key)
		if equity and equity[-1] == {}:
			net_equity += equity[-2].get(key)
		if provisional_profit_loss:
			net_provisional_profit_loss += provisional_profit_loss.get(key)

	return [
		{"value": net_asset, "label": _("Total Asset"), "datatype": "Currency", "currency": currency},
		{"value": net_liability, "label": _("Total Liability"), "datatype": "Currency", "currency": currency},
		{"value": net_equity, "label": _("Total Equity"), "datatype": "Currency", "currency": currency},
		{
			"value": net_provisional_profit_loss,
			"label": _("Provisional Profit / Loss (Credit)"),
			"indicator": "Green" if net_provisional_profit_loss > 0 else "Red",
			"datatype": "Currency",
			"currency": currency,
		},
	], (net_asset - net_liability + net_equity)


def get_chart_data(filters, columns, asset, liability, equity, currency):
	labels = [col.get("label") for col in columns[2:]]
	asset_data = [asset[-2].get(col.get("fieldname")) for col in columns[2:]] if asset else []
	liability_data = [liability[-2].get(col.get("fieldname")) for col in columns[2:]] if liability else []
	equity_data = [equity[-2].get(col.get("fieldname")) for col in columns[2:]] if equity else []

	datasets = []
	if asset_data:
		datasets.append({"name": _("Assets"), "values": asset_data})
	if liability_data:
		datasets.append({"name": _("Liabilities"), "values": liability_data})
	if equity_data:
		datasets.append({"name": _("Equity"), "values": equity_data})

	return {
		"type": "bar" if not filters.accumulated_values else "line",
		"data": {"labels": labels, "datasets": datasets},
		"fieldtype": "Currency",
		"options": "currency",
		"currency": currency,
	}
