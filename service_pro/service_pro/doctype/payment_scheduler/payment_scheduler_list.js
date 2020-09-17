frappe.listview_settings['Payment Scheduler'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		 if (doc.status === "Approved") {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};