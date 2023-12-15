frappe.ui.form.on('Lead', {
    refresh:function(frm) {
        frm.remove_custom_button('Opportunity','Create');
        frm.remove_custom_button('Quotation','Create');
        frm.add_custom_button(__('Opportunity'), function() {
            me.frm.trigger("make_opportunity_custom");
        }, __('Create'));
        frm.add_custom_button(__('Quotation'), () => {
            frappe.model.open_mapped_doc({
                method: "facilities_management_utility.facilities_management_utility.doc_event.quotation.make_quotation_from_lead",
                frm: cur_frm,
            })
        }, __('Create'));
    },
    make_opportunity_custom: async function(frm) {
		let existing_prospect = (await frappe.db.get_value("Prospect Lead",
			{
				"lead": frm.doc.name
			},
			"name", null, "Prospect"
		)).message.name;

		if (!existing_prospect) {
			var fields = [
				{
					"label": "Create Prospect",
					"fieldname": "create_prospect",
					"fieldtype": "Check",
					"default": 1
				},
				{
					"label": "Prospect Name",
					"fieldname": "prospect_name",
					"fieldtype": "Data",
					"default": frm.doc.company_name,
					"depends_on": "create_prospect"
				}
			];
		}
		let existing_contact = (await frappe.db.get_value("Contact",
			{
				"first_name": frm.doc.first_name || frm.doc.lead_name,
				"last_name": frm.doc.last_name
			},
			"name"
		)).message.name;

		if (!existing_contact) {
			fields.push(
				{
					"label": "Create Contact",
					"fieldname": "create_contact",
					"fieldtype": "Check",
					"default": "1"
				}
			);
		}

		if (fields) {
			var d = new frappe.ui.Dialog({
				title: __('Create Opportunity'),
				fields: fields,
				primary_action: function() {
					var data = d.get_values();
					frappe.call({
						method: 'create_prospect_and_contact',
						doc: frm.doc,
						args: {
							data: data,
						},
						freeze: true,
						callback: function(r) {
							if (!r.exc) {
								frappe.model.open_mapped_doc({
									method: "facilities_management_utility.facilities_management_utility.doc_event.lead.make_opportunity",
									frm: frm
								});
							}
							d.hide();
						}
					});
				},
				primary_action_label: __('Create')
			});
			d.show();
		} else {
			frappe.model.open_mapped_doc({
				method: "facilities_management_utility.facilities_management_utility.doc_event.lead.make_opportunity",
				frm: frm
			});
		}
	}
})


