# # Copyright (c) 2026, navaneeth and contributors
# # For license information, please see license.txt

# import frappe

# def execute(filters=None):
#     columns = [
#         {"label": "Status Category", "fieldname": "status_category", "fieldtype": "Data", "width": 200},
#         {"label": "Total Samples", "fieldname": "total_samples", "fieldtype": "html", "width": 150}
#     ]

#     # Count logic
#     completed_count = frappe.db.count("Soil Sample Collection", filters={"status": "Completed"})
#     pending_count = frappe.db.count("Soil Sample Collection", filters={
#         "status": ["not in", ["Completed", "Draft"]]
#     })

#     # Create the clickable links
#     completed_link = f'<a href="/app/soil-sample-collection?status=Completed"><b>{completed_count}</b></a>'
#     pending_url = '/app/soil-sample-collection?status=["not in", ["Completed", "Draft"]]'
#     pending_link = f'<a href=\'{pending_url}\'><b>{pending_count}</b></a>'

#     data = [
#         {"status_category": "Completed", "total_samples": completed_link},
#         {"status_category": "Pending", "total_samples": pending_link}
#     ]

#     return columns, data




import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Status Category",
            "fieldname": "status_category",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Total Samples",
            "fieldname": "total_samples",
            "fieldtype": "HTML",
            "width": 150
        }
    ]

    common_filters = {}

    if filters.get("from_date") and filters.get("to_date"):
        common_filters["date"] = [
            "between",
            [filters.get("from_date"), filters.get("to_date")]
        ]
        # Replace "date" with the actual date field in Soil Sample Collection

    completed_filters = {
        "status": "Completed",
        **common_filters
    }

    pending_filters = {
        "status": ["not in", ["Completed", "Draft"]],
        **common_filters
    }

    completed_count = frappe.db.count(
        "Soil Sample Collection",
        filters=completed_filters
    )

    pending_count = frappe.db.count(
        "Soil Sample Collection",
        filters=pending_filters
    )

    completed_link = (
        f'<a href="/app/soil-sample-collection?status=Completed">'
        f'<b>{completed_count}</b></a>'
    )

    pending_link = (
        f'<a href="/app/soil-sample-collection">'
        f'<b>{pending_count}</b></a>'
    )

    data = [
        {
            "status_category": "Completed",
            "total_samples": completed_link
        },
        {
            "status_category": "Pending",
            "total_samples": pending_link
        }
    ]

    return columns, data