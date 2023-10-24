frappe.ui.form.on('Contract', {
    refresh:function(frm) {
        frm.add_custom_button('Create Sales Invoice', () => {
            frappe.model.open_mapped_doc({
                method: "facilities_management_utility.facilities_management_utility.doc_event.contract.make_sales_invoice",
                frm: cur_frm
            })
        })
    }
})