frappe.ui.form.on('Quotation', {
    custom_get_items: function(frm){
        if(frm.doc.custom_auxiliary_item_template) {
            return frappe.call({
                method: 'facilities_management_utility.facilities_management_utility.doc_event.quotation.get_auxiliary_item',
                args: {
                    template_name: frm.doc.custom_auxiliary_item_template
                },
                callback: function(r) {
                   if(r.message){
                        r.message.forEach(function(element) {
							var c = frm.add_child("items");
							c.item_code = element.item;
                            c.item_name = element.item_name;
                            c.description = element.description;
                            c.uom = element.uom;
                            c.qty = 1;
                            c.rate = element.rate;
                            c.amount = c.qty * c.rate;
                            c.custom_is_billable = element.separate_billable;
                            c.custom_is_auxiliary_item = true;
						});
						refresh_field("items");
                   }
                }
            });
        }
        else{
            frappe.throw('Select Auxiliary Item Template')
        }
    }
});