
frappe.query_reports["New Customer"] = {
	"filters": [
		{
			"fieldname": "id",
			"label": __("ID"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "customer_name",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname": "territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory",
		},

	]
};