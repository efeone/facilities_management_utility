# Copyright (c) 2023, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from facilities_management_utility.facilities_management_utility.doc_event.quotation import set_quotation_item_rates

class AuxiliaryQuotation(Document):
	def on_update(self):
		quotation = frappe.get_doc("Quotation", self.quotation)
		set_quotation_item_rates(quotation)
		quotation.save()
		
@frappe.whitelist()
def get_auxiliary_item(item_template):
	child_table_data = frappe.get_all('Auxiliary Item',filters={'parent': item_template},
		fields=['item','rate']
	)
	return child_table_data
