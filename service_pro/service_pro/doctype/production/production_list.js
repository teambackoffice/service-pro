frappe.listview_settings['Production'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Bill", "To Deliver","To Deliver and Bill"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "blue", "status,=," + doc.status];
		} else if (["In Progress", "Partially Delivered"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (doc.status === "Completed") {
			// Closed
			return [__(doc.status), "green", "status,=,In Progress"];
		}

	},
};