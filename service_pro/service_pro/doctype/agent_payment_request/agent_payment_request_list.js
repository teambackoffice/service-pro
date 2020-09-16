frappe.listview_settings['Agent Payment Request'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Unpaid"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		}else if (doc.status === "Paid") {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};