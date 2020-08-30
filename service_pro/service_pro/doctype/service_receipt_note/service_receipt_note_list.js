frappe.listview_settings['Service Receipt Note'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Closed", "To Inspection","To Estimation", "To Production"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (doc.status === "Completed"){
            return [__(doc.status), "green", "status,=," + doc.status];
        }

	},
};