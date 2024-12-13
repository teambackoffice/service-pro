frappe.listview_settings['Inter Company Stock Transfer'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status === "In Transit" ) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		}else if (doc.status === "Received" ) {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};