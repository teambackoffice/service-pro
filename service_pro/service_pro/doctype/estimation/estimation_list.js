frappe.listview_settings['Estimation'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Quotation"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Closed","Completed"].includes(doc.status)){
            return [__(doc.status), "green", "status,=," + doc.status];
        }

	},
};