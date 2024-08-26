frappe.listview_settings['Sales Partner Payments'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		 if (["Unpaid"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (doc.status === "Partly Paid") {
			// Closed
			return [__(doc.status), "blue", "status,=," + doc.status];
		} else if (doc.status === "Paid") {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};