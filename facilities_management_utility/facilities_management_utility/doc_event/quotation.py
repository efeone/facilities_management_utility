import frappe
from datetime import datetime
from frappe.utils import time_diff
from frappe.model.mapper import get_mapped_doc
from frappe.email.doctype.notification.notification import get_context

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