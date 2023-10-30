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
def update_on_items(doc, method):
    if doc.custom_service_enquiry_items:
        for serviite_item in doc.custom_service_enquiry_items:
            serviite_item.item_code = get_the_item(serviite_item)


def get_the_item(serviite_item):
    item = frappe.db.exists("Item", {'custom_skill': serviite_item.skill_category, 'custom_gender': serviite_item.gender, 'custom_nationality': serviite_item.nationality})
    return item if item else ''
