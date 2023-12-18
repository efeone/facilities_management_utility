# Copyright (c) 2023, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AuxiliaryQuotation(Document):
	pass

@frappe.whitelist()
def get_auxiliary_item(item_template):
	child_table_data = frappe.get_all('Auxiliary Item',filters={'parent': item_template},
		fields=['item','rate']
	)
	return child_table_data
