frappe.listview_settings['Production'] = {
	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date",
		"per_delivered", "per_billed", "status", "order_type", "name", "skip_delivery_note"],
	get_indicator: function (doc) {
		if (doc.status === "In Progress") {
			// Closed
			return [__(doc.status), "orange", "status,=,In Progress"];
		} else if (doc.status === "Completed") {
			// Closed
			return [__(doc.status), "green", "status,=,In Progress"];
		}

	},
};