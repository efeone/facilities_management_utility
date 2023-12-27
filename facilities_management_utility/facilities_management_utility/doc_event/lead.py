import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_opportunity(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)

	target_doc = get_mapped_doc(
		"Lead",
		source_name,
		{
			"Lead": {
				"doctype": "Opportunity",
				"field_map": {
					"campaign_name": "campaign",
					"doctype": "opportunity_from",
					"name": "party_name",
					"lead_name": "contact_display",
					"company_name": "customer_name",
					"email_id": "contact_email",
					"mobile_no": "contact_mobile",
					"lead_owner": "opportunity_owner",
					"notes": "notes",
				},
			},
			"Service Enquiry Item": {
				"doctype": "Service Enquiry Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					"stock_uom": "stock_uom",
					"item_code": "item_code",
					"no_of_resources": "no_of_resources",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	return target_doc

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

@frappe.whitelist()
def create_or_set_item(doc, method=None):
	doc.custom_total_resources = 0
	for service_item in doc.custom_service_enquiry_items:
		doc.custom_total_resources += service_item.no_of_resources
		item_code = service_item.skill_category + '-' + service_item.nationality + '-' + service_item.gender
		item = frappe.db.exists('Item', item_code)
		if item:
			service_item.item_code = item
		else:
			new_item = frappe.new_doc('Item')
			new_item.item_code = item_code
			new_item.item_name = service_item.skill_category
			new_item.item_group = frappe.db.get_default('Item Group')
			new_item.custom_skill = service_item.skill_category
			new_item.custom_nationality = service_item.nationality
			new_item.custom_gender = service_item.gender
			new_item.save()
			service_item.item_code = new_item.name
			