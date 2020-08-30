frappe.listview_settings['Service Receipt Note'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if ([ "To Inspection","To Estimation", "To Production"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Closed","Completed"].includes(doc.status)){
            return [__(doc.status), "green", "status,=," + doc.status];
        }

	},
};