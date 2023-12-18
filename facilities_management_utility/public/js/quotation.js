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
    custom_employee_details: function (frm, cdt, cdn) {
        var quotation_name = frm.doc.name;
        var child = locals[cdt][cdn];
        var selected_item_code = child.item_code;

        frappe.call({
            method: 'facilities_management_utility.facilities_management_utility.doc_event.quotation.get_auxiliary_quotation_data',
            args: {
                quotation_name: quotation_name,
                item_code: selected_item_code
            },
            callback: function (response) {
                var auxiliaryData = response.message;

                if (auxiliaryData) {
                    var employee_dialog = new frappe.ui.Dialog({
                        title: 'Table-Test',
                        size: "extra-large",
                        fields: [
                            {
                                fieldtype: 'HTML',
                                fieldname: 'table_section'
                            }
                        ],
                        primary_action_label: 'Update',
                        primary_action: function () {
                          var tableRows = employee_dialog.fields_dict.table_section.$wrapper.find('tbody tr');

                          var updatedData = [];

                          // Loop through each table row to collect the updated values
                          tableRows.each(function (index, row) {
                              var rowData = {};

                              // Retrieve the employee value from the first cell (assuming it's the first cell in the row)
                              var employee = $(row).find('td:first').text().trim();

                              // Retrieve input values from each cell in the row
                              $(row).find('td').each(function (cellIndex, cell) {
                                  var columnName = keys[cellIndex]; // Get the corresponding column name from keys array
                                  var cellValue = $(cell).find('input').val(); // Retrieve the input value from the cell

                                  // Store the cell value with the corresponding column name
                                  rowData[columnName] = cellValue;
                              });
                              rowData['employee'] = employee;
                              updatedData.push(rowData);
                          });
                          frappe.call({
                              method: 'facilities_management_utility.facilities_management_utility.doc_event.quotation.update_auxiliary_quotation_data',
                              args: {
                                  quotation_name: quotation_name,
                                  item_code:selected_item_code,
                                  updated_data: updatedData
                              },
                              callback: function (response) {
                                  employee_dialog.hide();
                                  if(response.message){
                                    frappe.throw(response.message);
                                  }
                              }
                          });
                        }
                    });

                    // Define the HTML structure for the editable table
                    var tableHTML = `
                    <style>
                        th, td {
                          min-width: min-content;
                        }
                        td input {
                          width: 100%;
                          box-sizing: border-box;
                        }
                    </style>
                    <div style="overflow:scroll;">
                        <table border="1">
                            <thead min-width="100px">
                                <tr>`;

                    // Generate table headers based on keys in the first object of auxiliaryData
                    var keys = Object.keys(auxiliaryData[0]);
                    keys.forEach(function (key) {
                        tableHTML += `<th>${key}</th>`;
                    });

                    tableHTML += `</tr></thead><tbody>`;

                    // Populate editable table rows with data
                    auxiliaryData.forEach(function (dataRow) {
                        tableHTML += '<tr>';
                        keys.forEach(function (key) {
                            if (key === 'employee') {
                                tableHTML += `<td>${dataRow[key]}</td>`;
                            } else {
                                tableHTML += `<td><input type="text" value="${dataRow[key]}"></td>`;
                            }
                        });
                        tableHTML += '</tr>';
                    });

                    // Close the table HTML
                    tableHTML += `
                            </tbody>
                        </table>
                    </div>
                    `;

                    // Show the dialog and set HTML content
                    employee_dialog.show();
                    employee_dialog.fields_dict.table_section.$wrapper.html(tableHTML);
                }
            },
        });
    },
});
