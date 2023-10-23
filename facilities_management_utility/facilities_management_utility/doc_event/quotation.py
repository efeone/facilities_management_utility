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

@frappe.whitelist()
def create_customer_from_qtn(doc, method):
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
        contract = frappe.new_doc('Contract')
        contract.party_type = 'Customer'
        contract.party_name = customer
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
        contract.save(ignore_permissions=True)