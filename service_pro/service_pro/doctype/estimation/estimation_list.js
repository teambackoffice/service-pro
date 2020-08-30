frappe.listview_settings['Estimation'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Closed", "To Production"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (doc.status === "Completed"){
            return [__(doc.status), "green", "status,=," + doc.status];
        }

	},
};