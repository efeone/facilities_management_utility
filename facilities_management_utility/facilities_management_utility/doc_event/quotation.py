import frappe
from datetime import datetime
from frappe.utils import time_diff
from frappe.model.mapper import get_mapped_doc
from frappe.email.doctype.notification.notification import get_context
from frappe.utils import (
	cint,
	create_batch,
	cstr,
	flt,
	formatdate,
	get_number_format_info,
	getdate,
	now,
    today,
	nowdate,
    add_days,
    add_years
)

from erpnext.setup.utils import get_exchange_rate
import json

@frappe.whitelist()
def create_customer_from_qtn(doc, method):
    if doc.workflow_state == 'Client Accepted':
        if doc.quotation_to == 'Lead':
            lead = frappe.get_doc('Lead', doc.party_name)
            customer = frappe.new_doc('Customer')
            if lead.company_name:
                customer.customer_type = 'Company'
                customer.customer_name = lead.company_name
            else:
                customer.customer_type = 'Individual'
                customer.customer_name = lead.lead_name
            customer.customer_group = frappe.db.get_default("Customer Group")
            customer.territory = frappe.db.get_default("Territory")
            lead_name = lead.name
            address = frappe.get_all(
                "Dynamic Link",
                {
                    "link_doctype": lead.doctype,
                    "link_name": lead.name,
                    "parenttype": "Address",
                },
                ["parent"],
                limit=1,
            )

            contact = frappe.get_all(
                "Dynamic Link",
                {
                    "link_doctype": lead.doctype,
                    "link_name": lead.name,
                    "parenttype": "Contact",
                },
                ["parent"],
                limit=1,
            )

            if address:
                customer.customer_address = address[0].parent

            if contact:
                customer.contact_person = contact[0].parent
            customer.save()
            if customer.name:
                create_contract_from_qtn(doc, customer)

@frappe.whitelist()
def get_auxiliary_item(template_name):
    query = """
        SELECT
            item,
            item_name,
            separate_billable,
            uom,
            description
        FROM
            `tabAuxiliary Item`
        WHERE
            parent = '{field}'
    """.format(field = template_name)
    aux_item = frappe.db.sql(query, as_dict = 1)
    return aux_item


frappe.whitelist()
def create_contract_from_qtn(doc, customer):
    if customer:
        lead = frappe.get_doc('Lead', doc.party_name)
        contract = frappe.new_doc('Contract')
        contract.party_type = 'Customer'
        contract.party_name = customer
        contract.custom_organization_name = lead.company_name
        contract.custom_position = lead.job_title
        contract.custom_email = lead.email_id
        contract.custom_mobile_no = lead.mobile_no
        contract.document_type = 'Quotation'
        contract.document_name = doc.name
        contract.start_date = today()
        if doc.custom_contract_period == '1 Year':
            contract.end_date = add_years(today(), 1)
        elif doc.custom_contract_period == '2 Year':
            contract.end_date = add_years(today(), 2)
        elif doc.custom_contract_period == '3 Year':
            contract.end_date = add_years(today(), 3)
        elif doc.custom_contract_period == '4 Year':
            contract.end_date = add_years(today(), 4)
        elif doc.custom_contract_period == '5 Year':
            contract.end_date = add_years(today(), 5)
        contract.contract_template = doc.custom_contract_template
        contract.contract_terms = frappe.get_value('Contract Template', contract.contract_template, 'contract_terms')
        for item in doc.items:
            contract.append('custom_items', {
                'item': item.item_code,
            })
        contract.save(ignore_permissions=True)
        if contract.name:
            create_project_from_contract(contract)


@frappe.whitelist()
def make_quotation_from_lead(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)
	print(source_name)
	target_doc = get_mapped_doc(
		"Lead",
		source_name,
		{
			"Lead": {
                    "doctype": "Quotation",
                    "field_map": {"name": "party_name"},
            },
			"Service Enquiry Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					'item_code':'item_code',
					'no_of_resources':'qty'
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)
	# source_doc = frappe.get_doc('Lead', source_name)

	target_doc.quotation_to = "Lead"
	target_doc.custom_auxiliary_value_template = "Auxiliary Values"
	target_doc.run_method("set_missing_values")
	target_doc.run_method("set_other_charges")
	target_doc.run_method("calculate_taxes_and_totals")

	target_doc = fetch_and_map_auxiliary_values(target_doc, "Auxiliary Values")

	return target_doc

@frappe.whitelist()
def make_quotation_from_opportunity(source_name, target_doc=None):
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		if not source.get("items", []):
			quotation.opportunity = source.name

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Quotation",
				"field_map": {"opportunity_from": "quotation_to", "name": "enq_no", "source": "coupon_code"},
			},
			"Service Enquiry Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					"uom": "stock_uom",
					"item_code": "item_code",
					"no_of_resources": "qty",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)
	doclist.custom_auxiliary_value_template = "Auxiliary Values"
	# Call the function to fetch and map auxiliary values
	doclist = fetch_and_map_auxiliary_values(doclist, "Auxiliary Values")

	return doclist

def fetch_and_map_auxiliary_values(doctype, template):
    if doctype.custom_auxiliary_value_template == template:
        # Fetch child table data from Auxiliary Value Template
        auxiliary_values = frappe.get_all("Auxiliary Values And Benefits",
                                          filters={"parent": "Auxiliary Values"},
                                          fields=["item_description", "client_company_name"])

        for aux_value in auxiliary_values:
            # Map fetched values to Quotation Item child table
            auxiliary_values = doctype.append("custom_auxiliary_value")
            auxiliary_values.item_description = aux_value.item_description
            auxiliary_values.client_company_name = aux_value.client_company_name
            # Add additional mapping as needed

    return doctype

def _set_missing_values(source, target):
	address = frappe.get_all(
		"Dynamic Link",
		{
			"link_doctype": source.doctype,
			"link_name": source.name,
			"parenttype": "Address",
		},
		["parent"],
		limit=1,
	)

	contact = frappe.get_all(
		"Dynamic Link",
		{
			"link_doctype": source.doctype,
			"link_name": source.name,
			"parenttype": "Contact",
		},
		["parent"],
		limit=1,
	)

	if address:
		target.customer_address = address[0].parent

	if contact:
		target.contact_person = contact[0].parent

def create_project_from_contract(contract):
     if contract:
        project = frappe.new_doc('Project')
        project.customer = contract.party_name
        project.custom_contract = contract.name
        project.project_name = 'Project' + contract.party_name
        project.expected_start_date = contract.start_date
        project.expected_end_date = contract.end_date
        project.save(ignore_permissions=True)

@frappe.whitelist()
def get_auxiliary_quotation_data(quotation_name, item_code):
    auxiliary_quotation_data = frappe.get_all(
        'Auxiliary Quotation',
        filters={'quotation': quotation_name, 'item_code': item_code},
        fields=['name', 'employee'],
        order_by='employee asc'
    )

    # Fetch 'item' and 'amount' from 'Auxiliary Quotation Item'
    for auxiliary_quotation in auxiliary_quotation_data:
        auxiliary_quotation_item_data = frappe.get_all(
            'Auxiliary Quotation Item',
            filters={'parent': auxiliary_quotation.get('name')},
            fields=['item', 'amount'],
            order_by='item asc'
        )
        temp_dict = auxiliary_quotation.copy()
        temp_dict.pop('name')
        temp_dict['Employee'] = temp_dict['employee'].capitalize()
        temp_dict.pop('employee')

        # Add items from auxiliary_quotation_item_data to the dictionary
        for item in auxiliary_quotation_item_data:
            temp_dict[item['item']] = item['amount']

        # Update the dictionary in auxiliary_quotation_data with the modified temp_dict
        auxiliary_quotation.clear()
        auxiliary_quotation.update(temp_dict)

    return auxiliary_quotation_data

@frappe.whitelist()
def update_auxiliary_quotation_data(quotation_name,item_code, updated_data):
	input_data = json.loads(updated_data)
	for row_data in input_data:
		employee = row_data.get('Employee')

		if employee:
			converted_data = []
			for item, amount in row_data.items():
				if item != 'Employee':
					converted_data.append({'item': item, 'amount': float(amount)})

			# Fetch the Auxiliary Quotation based on item_code and employee
			auxiliary_quotations = frappe.get_all('Auxiliary Quotation',
				filters={'quotation': quotation_name,'item_code': item_code, 'employee': employee},
				fields=['name']
			)

			# Update Auxiliary Quotation Item with the converted data amounts
			for data in converted_data:
				item_name = frappe.get_value('Auxiliary Quotation Item',
					filters={'parent': auxiliary_quotations[0]['name'], 'item': data['item']},
					fieldname='name'
				)
				if item_name:
					# Update the amount for each item in converted_data
					frappe.db.set_value('Auxiliary Quotation Item', item_name, 'amount', data['amount'])

	frappe.db.commit()
	return "Data updated successfully"

def create_auxiliary_quotation(quotation, item_code, employee, template):
    aux_quotation_items = frappe.get_all('Auxiliary Item',filters={'parent': template},
		fields=['item','rate']
	)
    aux_quotation = frappe.new_doc("Auxiliary Quotation")
    aux_quotation.quotation = quotation
    aux_quotation.item_code = item_code
    aux_quotation.employee = employee
    aux_quotation.auxiliary_item_template = template
    for item in aux_quotation_items:
        row = aux_quotation.append("auxiliary_quotation_item")
        row.item = item.item
        row.amount = item.rate
    aux_quotation.save()

@frappe.whitelist()
def create_auxiliary_quotations(doc, method=None):
    items = doc.items
    for item in items:
        for i in range (1, int(item.qty)+1):
            employee = "Employee " + str(i)
            create_auxiliary_quotation(doc.name, item.item_code, employee, doc.custom_contract_template)

@frappe.whitelist()
def get_auxiliary_values(item_template):
	child_table_data = frappe.get_all('Auxiliary Values And Benefits',filters={'parent': item_template},
		fields=['item_description','client_company_name']
	)
	return child_table_data
