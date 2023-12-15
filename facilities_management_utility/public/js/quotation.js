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

frappe.ui.form.on('Quotation Item', {
    custom_employee_details: function (frm) {
        var employee_dialog = new frappe.ui.Dialog({
            title: 'Table-Test',
            size: "extra-large",
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'table_section'
                }
            ],
            // primary_action_label: 'Close',
            // primary_action: function() {
            //     employee_dialog.hide();
            // }
        });
        // Define the HTML structure for the table
        var tableHTML = `
        <div>
            <table border="1">
                <thead>
                    <tr>
                        <th>Employee</th>
                        <th>Staff Contract salary</th>
                        <th>Overtime</th>
                        <th>Food</th>
                        <th>Housing & Transport to/from work</th>
                        <th>Visa/Transfer, Iqama & Labor card</th>
                        <th>GOSI</th>
                        <th>Medical Insurance (Class C)</th>
                        <th>Vacation (21days/Year) / Gratuity (EOSB)</th>
                        <th>Workers  Air Travel expenses</th>
                        <th>Uniform</th>
                        <th>Recruitment, Visa processing</th>
                        <th>Exit Re entry</th>
                        <th>Baladiya, Drivers License or Any other government registrations</th>
                        <th>VAT. Taxes, COC, MOFA</th>
                        <th>Quarantine or PCR Cost on Arrival</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>E1</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                        <td>Data 2</td>
                    </tr>
                </tbody>
            </table>
        </div>
        `;
        employee_dialog.show();
        // Set the HTML content of the field in the dialog
        employee_dialog.fields_dict.table_section.$wrapper.html(tableHTML);
    },
});


