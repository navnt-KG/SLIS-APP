
import frappe
import json
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

                        try:

                            bulk_data = json.loads(
                                bulk_row.values_json or "{}"
                            )

                            final_data = {}

                            for test_name, test_value in bulk_data.items():

                                if isinstance(
                                    test_value,
                                    dict
                                ):

                                    final_data[test_name] = (
                                        test_value.get(
                                            "result",
                                            0
                                        )
                                    )

                                else:

                                    final_data[test_name] = (
                                        test_value
                                    )

                            test_row.values_json = json.dumps(
                                final_data
                            )

                            updated = True

                        except Exception:

                            test_row.values_json = (
                                bulk_row.values_json
                            )

                            updated = True

            if updated:

                doc.save(
                    ignore_permissions=True
                )