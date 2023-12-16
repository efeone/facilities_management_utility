// Copyright (c) 2023, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Auxiliary Quotation', {
	// refresh: function(frm) {

	// }
  auxiliary_item_template: function (frm) {
    get_auxiliary_item(frm);
  }
});

let get_auxiliary_item = function (frm){
  frappe.call({
    method:'facilities_management_utility.facilities_management_utility.doctype.auxiliary_quotation.auxiliary_quotation.get_auxiliary_item',
    args: {
      item_template: frm.doc.auxiliary_item_template
    },
    callback: function(r) {
      if (r.message && r.message.length > 0) {
        frm.clear_table('auxiliary_quotation_item');
        r.message.forEach(item => {
          let auxiliary_quotation_item = frm.add_child('auxiliary_quotation_item');
          auxiliary_quotation_item.item = item.item;
          auxiliary_quotation_item.amount = item.rate;
        });
        frm.refresh_field('auxiliary_quotation_item');
      }
    }
  })
}
