# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document


# class SoilSampleCollection(Document):
# 	pass

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SoilSampleCollection(Document):

    def validate(self):
        # Total number of samples = number of child rows
        self.total_samples = len(self.bulk_samples or [])

    def before_save(self):
        prefix_map = {
            "Farmer": "FS",
            "Consultancy": "CS",
            "Department": "DS"
        }

        prefix = prefix_map.get(self.sample_type)
        if not prefix:
            return

        for row in self.bulk_samples:
            if not row.sample_id:
                row.sample_id = make_autoname(f"{prefix}-.###")


@frappe.whitelist()
def add_to_lab_register(docname):
    doc = frappe.get_doc("Soil Sample Collection", docname)

    if doc.lab_register_created:
        frappe.throw("Already added to the Lab Register")

    first_lab = None
    created = 0

    for row in doc.bulk_samples:
        lab = frappe.new_doc("Lab Register")
        lab.sample_id = row.sample_id
        lab.latitude = row.latitude
        lab.longitude = row.longitude
        lab.package = row.package
        lab.source = row.source
        lab.sample_type = doc.sample_type
        lab.soil_sample_collection = doc.name

        lab.insert(ignore_permissions=True)

        if not first_lab:
            first_lab = lab.name

        created += 1

    # IMPORTANT: use db.set_value
    frappe.db.set_value(
        "Soil Sample Collection",
        doc.name,
        {
            "lab_register_created": 1,
            "lab_register_ref": first_lab
        }
    )

    return {
        "created": created,
        "lab_register": first_lab
    }

		
