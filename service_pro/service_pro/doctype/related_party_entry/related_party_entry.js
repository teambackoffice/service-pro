// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Related Party Entry', {
	refresh:function(frm){
		if(frm.doc.docstatus == 1){
			if(frm.doc.status == "Unpaid"){
				frm.add_custom_button(__("Payment"), function(){
					frappe.confirm(__("Are you sure want to create payment?"),
						function(){
							frappe.call({
								method:"create_journal_entry",
								doc:frm.doc,
								callback:function(r){
									frappe.msgprint("Journal Entry Created successfully.")
									frm.reload_doc();
								}
							});
						}
					)
				}, __("Create"))
			}
			else if(frm.doc.status == "Paid" || frm.doc.status == "Partially Returned"){
				frm.add_custom_button(__("Return"), function(){
					var dialog = new frappe.ui.Dialog({
						title:"Return",
						fields:[
							{
								label: "Return Date",
								fieldname: "return_date",
								fieldtype: "Date",
								default:frappe.datetime.get_today(),
								reqd:1
							},
							{
								label: "Returned From",
								fieldname: "returned_from",
								fieldtype: "Link",
								options: "Account",
								reqd:1,
								get_query: () => {
									return {
										query:"service_pro.service_pro.doctype.related_party_entry.related_party_entry.accounts_query",
										filters:{
											is_group:false,
											field: "Returned From",
											root_type:"'Asset'",
											account_type : "'Bank', 'Cash'"
										}
									}
								}
							},
							{
								label: "Return Amount",
								fieldname: "return_amount",
								fieldtype: "Currency",
								default: frm.doc.pending_amount || frm.doc.amount,
								reqd:1
							}
						],
						primary_action: () => {
							const args = dialog.get_values()
							dialog.hide();
							frappe.call({
								method: "service_pro.service_pro.doctype.related_party_entry.related_party_entry.create_return_entry",
								args:{
									related_party_entry: frm.doc.name,
									return_date: args.return_date,
									returned_from: args.returned_from,
									return_amount: args.return_amount
								},
								callback:function(r){
									frm.reload_doc();
								}
							})
						},
						primary_action_label: __('Confirm')
					});
					dialog.show();
				}, __("Create"))
			}
		}
	},
	onload:function(frm){
		frm.set_query("related_party_account", function(){
			return {
				query:"service_pro.service_pro.doctype.related_party_entry.related_party_entry.accounts_query",
				filters:{
					is_group:false,
					field:"Related Party Account",
					root_type:"'Asset', 'Liability'"
				}
			}
		});
		frm.set_query("account_for_payments", function(){
			return {
				query:"service_pro.service_pro.doctype.related_party_entry.related_party_entry.accounts_query",
				filters:{
					is_group:false,
					field: "Account For Payments",
					root_type:"'Asset'",
					account_type : "'Bank', 'Cash'"
				}
			}
		});
	},
	before_save:function(frm){
		frm.trigger("calculateTotalexpanse");
	},
	calculateTotalexpanse:function(frm){
		let total = 0;
		frm.doc.related_party_entry_expanse_list.forEach(el=>{
			total +=el.amount;
		});
		frm.set_value("amount", total);
	}
});

frappe.ui.form.on('Related Party Entry Expanse List', {
	amount:function(frm){
		frm.trigger("calculateTotalexpanse");
	},
	related_party_entry_expanse_list_remove:function(frm){
		frm.trigger("calculateTotalexpanse");
	}
});
