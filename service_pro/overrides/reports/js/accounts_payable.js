frappe.query_reports["Accounts Payable"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company"),
			on_change: () => {
				var company = frappe.query_report.get_filter_value('company');
				if (company) {
					frappe.db.get_value('Company', company, ["custom_bank_details_for_report"], function(value) {

						frappe.query_report.set_filter_value('company_address', value["custom_bank_details_for_report"]);
					});


				}
			}
		},
		{
			"fieldname": "company_address",
			"label": __("Company Address"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "report_date",
			"label": __("Posting Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book"
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Autocomplete",
			options: get_party_type_options(),
			on_change: function() {
				frappe.query_report.set_filter_value('party', "");
				frappe.query_report.toggle_filter_display('customer_group', frappe.query_report.get_filter_value('party_type') !== "Customer");
			}
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value('party_type');
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			},
			on_change: () => {
				var customer = frappe.query_report.get_filter_value('party')[0];
				var party_type = frappe.query_report.get_filter_value('party_type');
				console.log("PARRTY TYPE")
				console.log(party_type)
				var company = frappe.query_report.get_filter_value('company');
				if (customer && party_type === 'Customer') {
					a = []
					frappe.call({
						method: "service_pro.crud_events.party.get_party_details",
						args: {
							"party": customer,
							"party_type": party_type
						},
						callback: function (r) {
							$.each(r.message, function(k, v) {
							if(v != null)
								a.push(v)
								console.log(a)
							frappe.query_report.set_filter_value('customer_address', a);
							});
						}
					});
					if(party_type === 'Customer'){
						frappe.db.get_value('Customer', customer, ["tax_id", "customer_name", "payment_terms"], function(value) {
						frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
						frappe.query_report.set_filter_value('customer_name', value["customer_name"]);
						frappe.query_report.set_filter_value('payment_terms', value["payment_terms"]);
						});

						frappe.db.get_value('Customer Credit Limit', {'parent': customer, 'company': company},
							["credit_limit"], function(value) {
							if (value) {
								frappe.query_report.set_filter_value('credit_limit', value["credit_limit"]);
							}
						}, "Customer");
					}

				} else {
					frappe.query_report.set_filter_value('tax_id', "");
					frappe.query_report.set_filter_value('customer_name', "");
					frappe.query_report.set_filter_value('credit_limit', "");
					frappe.query_report.set_filter_value('payment_terms', "");
				}
			}
		},
		{
			"fieldname":"customer_address",
			"label": __("Customer Address"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "party_account",
			"label": __("Receivable Account"),
			"fieldtype": "Link",
			"options": "Account",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company,
						'account_type': 'Receivable',
						'is_group': 0
					}
				};
			}
		},
		{
			"fieldname": "ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nDue Date',
			"default": "Due Date"
		},
		{
			"fieldname": "range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"reqd": 1
		},
		{
			"fieldname": "range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"reqd": 1
		},
		{
			"fieldname": "range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"reqd": 1
		},
		{
			"fieldname": "range4",
			"label": __("Ageing Range 4"),
			"fieldtype": "Int",
			"default": "120",
			"reqd": 1
		},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname": "payment_terms_template",
			"label": __("Payment Terms Template"),
			"fieldtype": "Link",
			"options": "Payment Terms Template"
		},
		{
			"fieldname": "sales_partner",
			"label": __("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory"
		},
		{
			"fieldname": "group_by_party",
			"label": __("Group By Customer"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "based_on_payment_terms",
			"label": __("Based On Payment Terms"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "show_future_payments",
			"label": __("Show Future Payments"),
			"fieldtype": "Check",
			"default" : 1,
		},
		{
			"fieldname": "show_delivery_notes",
			"label": __("Show Linked Delivery Notes"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "show_sales_person",
			"label": __("Show Sales Person"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "tax_id",
			"label": __("Tax Id"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "show_remarks",
			"label": __("Show Remarks"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "customer_name",
			"label": __("Customer Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "payment_terms",
			"label": __("Payment Tems"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "credit_limit",
			"label": __("Credit Limit"),
			"fieldtype": "Currency",
			"hidden": 1
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	},

	onload: function(report) {
		report.page.add_inner_button(__("Accounts Receivable Summary"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Accounts Receivable Summary', {company: filters.company});
		});
	}
}

erpnext.utils.add_dimensions('Accounts Receivable', 9);

function get_party_type_options() {
	let options = [];
	frappe.db.get_list(
		"Party Type", {filters:{"account_type": "Receivable"}, fields:['name']}
	).then((res) => {
		res.forEach((party_type) => {
			options.push(party_type.name);
		});
	});
	return options;
}