frappe.ui.form.on('Opportunity', {
    refresh:function(frm) {
        frm.remove_custom_button('Quotation','Create');
        frm.add_custom_button(__('Quotation'), () => {
            frappe.model.open_mapped_doc({
                method: "facilities_management_utility.facilities_management_utility.doc_event.quotation.make_quotation_from_opportunity",
                frm: cur_frm,
            })
        }, __('Create'));
    }
})


