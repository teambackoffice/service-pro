frappe.listview_settings["Service Order Form"] = {
	get_indicator: function (doc) {
		if (doc.status === "Converted") {
			// Closed
			return [__("Converted"), "green", "status,=,Converted"];
		}
		else if (doc.status === "Open") {
			return [__("Open"), "red", "status,=,Open"];
		}
		else if (doc.status === "Expired") {
			return [__("Expired"), "yellow", "status,=,Expired"];
		} 
	},
}