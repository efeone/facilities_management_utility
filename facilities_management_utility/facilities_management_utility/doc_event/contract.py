import frappe
from datetime import datetime
from frappe.utils import time_diff
from frappe.model.mapper import get_mapped_doc
from frappe.email.doctype.notification.notification import get_context
from erpnext.projects.doctype.timesheet.timesheet import get_projectwise_timesheet_data

@frappe.whitelist()
def make_sales_invoice(contract):
    if contract:
        contract_doc = frappe.get_doc('Contract', contract)
        target = frappe.new_doc("Sales Invoice")
        project = frappe.db.get_value('Project', {'custom_contract': contract}, "name")
        project_doc = frappe.get_doc('Project', project)
        target.company = project_doc.company
        if project_doc.customer:
            target.customer = project_doc.customer

        # if project_doc.currency:
        #     target.currency = project_doc.currency
        
        for item in contract_doc.custom_items:
            if item.employee:
                if project:
                    for data in get_projectwise_timesheet_data_with_employee(project, item.employee):
                        target.append(
                            "timesheets",
                            {
                                "time_sheet": data.time_sheet,
                                "billing_hours": data.billing_hours,
                                "billing_amount": data.billing_amount,
                                "timesheet_detail": data.name,
                                "activity_type": data.activity_type,
                                "description": data.description,
                            },
                        )
                        billing_rate = frappe.db.get_value('Resource Schedule', {'resource': item.employee, 'project':project}, 'rate')
                        if item.item:
                            target.append("items", {"item_code": item, "qty": data.billing_hours, "rate": billing_rate})

        target.save(ignore_permissions=True)
        return target
@frappe.whitelist()
def get_projectwise_timesheet_data_with_employee(project=None, employee=None, from_time=None, to_time=None):
    condition = ""
    if project:
        condition += "AND tsd.project = %(project)s "
    if employee:
        condition += "AND ts.employee = %(employee)s "

    query = f"""
		SELECT
			tsd.name as name,
			tsd.parent as time_sheet,
			tsd.from_time as from_time,
			tsd.to_time as to_time,
			tsd.billing_hours as billing_hours,
			tsd.billing_amount as billing_amount,
			tsd.activity_type as activity_type,
			tsd.description as description,
			ts.currency as currency,
			tsd.project_name as project_name
		FROM `tabTimesheet Detail` tsd
			INNER JOIN `tabTimesheet` ts
			ON ts.name = tsd.parent
		WHERE
			tsd.parenttype = 'Timesheet'
			AND tsd.docstatus = 1
			AND tsd.is_billable = 1
			AND tsd.sales_invoice is NULL
			{condition}
		ORDER BY tsd.from_time ASC
	"""

    filters = {"project": project, "employee": employee}
    return frappe.db.sql(query, filters, as_dict=1)
