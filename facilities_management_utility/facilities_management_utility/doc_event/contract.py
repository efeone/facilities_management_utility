import frappe
from datetime import datetime
from frappe.utils import time_diff
from frappe.model.mapper import get_mapped_doc
from frappe.email.doctype.notification.notification import get_context

@frappe.whitelist()
def create_contract_from_qtn(customer, qtn):
    if customer:
        contract = frappe.new_doc('Contract')
        contract.party_type = 'Customer'
        contract.party_name = customer
        contract.

