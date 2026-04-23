# # Copyright (c) 2026, navaneeth and contributors
# # For license information, please see license.txt

# import frappe

# def execute(filters=None):
#     # Defining columns
#     columns = [
#         {"label": "Sl. No", "fieldname": "idx", "fieldtype": "Int", "width": 80},
#         {"label": "Scheme Name", "fieldname": "scheme_name", "fieldtype": "Data", "width": 250},
#         {"label": "Number of Samples", "fieldname": "sample_count", "fieldtype": "html", "width": 150}
#     ]

#     # 1. Dynamically fetch all unique scheme names from the database
#     # We filter out empty/null values to keep the report clean
#     schemes = frappe.get_all("Soil Sample Collection", 
#         fields=["distinct scheme_name"], 
#         filters={"scheme_name": ["not in", ["", None]]},
#         order_by="scheme_name asc"
#     )

#     data = []

#     for i, row in enumerate(schemes, start=1):
#         scheme = row.scheme_name
        
#         # 2. Count samples for this specific scheme
#         count = frappe.db.count("Soil Sample Collection", filters={"scheme_name": scheme})

#         # 3. Create the clickable link to the list view
#         link = f'<a href="/app/soil-sample-collection?scheme_name={scheme}"><b>{count}</b></a>'

#         data.append({
#             "idx": i,
#             "scheme_name": scheme,
#             "sample_count": link
#         })

#     return columns, data



# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    # 1. Defining columns
    columns = [
        {"label": _("Sl. No"), "fieldname": "idx", "fieldtype": "Int", "width": 80},
        {"label": _("Scheme Name"), "fieldname": "scheme_name", "fieldtype": "Data", "width": 250},
        {"label": _("Number of Samples"), "fieldname": "sample_count", "fieldtype": "Int", "width": 150}
    ]

    # 2. Fetch grouped data directly from the database
    # This filters by 'Scheme' and counts samples grouped by 'name_of_type'
    report_data = frappe.get_all("Soil Sample Collection", 
        fields=[
            "name_of_type as scheme_name", 
            "count(name) as sample_count"
        ], 
        filters={
            "type_of_collection": "Scheme",
            "name_of_type": ["not in", ["", None]]
        },
        group_by="name_of_type",
        order_by="name_of_type asc"
    )

    # 3. Format the data for the report table
    data = []
    for i, row in enumerate(report_data, start=1):
        data.append({
            "idx": i,
            "scheme_name": row.scheme_name,
            "sample_count": row.sample_count
        })

    return columns, data