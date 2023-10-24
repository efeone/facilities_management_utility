frappe.ui.form.on('Lead', {
    refresh:function(frm) {
        frm.add_custom_button('Create Quotation', () => {
            frappe.model.open_mapped_doc({
                method: "facilities_management_utility.facilities_management_utility.doc_event.quotation.make_quotation",
                frm: cur_frm
            })
        })
    }
})


