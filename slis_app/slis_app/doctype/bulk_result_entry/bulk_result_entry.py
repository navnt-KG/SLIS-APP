# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.model.document import Document


class BulkResultEntry(Document):

    def on_update(self):

        soil_results = frappe.get_all(
            "Soil Test Result",
            fields=["name"]
        )

        for soil_result in soil_results:

            doc = frappe.get_doc(
                "Soil Test Result",
                soil_result.name
            )

            updated = False

            for test_row in doc.test_sample_data:

                for bulk_row in self.sample_data:

                    if (
                        test_row.sample_id
                        == bulk_row.sample_id
                    ):

                        test_row.values_json = (
                            bulk_row.values_json
                        )

                        updated = True

            if updated:

                doc.save(
                    ignore_permissions=True
                )