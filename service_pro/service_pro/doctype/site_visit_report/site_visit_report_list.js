frappe.listview_settings['Site Visit Report'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status === "Completed" ) {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};