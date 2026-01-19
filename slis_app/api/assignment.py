import frappe
from frappe.desk.search import search_link as default_search_link

@frappe.whitelist()
def filtered_user_search(*args, **kwargs):
    """
    Restrict Assigned To users based ONLY on Reports To (Senior)
    """

    # Remove internal frappe argument
    kwargs.pop("cmd", None)

    # Extract values
    doctype = kwargs.get("doctype") or (args[0] if len(args) > 0 else None)
    txt = kwargs.get("txt") or (args[1] if len(args) > 1 else "")
    start = kwargs.get("start", 0)
    page_len = kwargs.get("page_len", 20)

    # Apply only for User search
    if doctype != "User":
        return default_search_link(*args, **kwargs)

    # Logged-in senior user
    senior_user = frappe.session.user

    # Find senior employee
    senior_emp = frappe.db.get_value(
        "Employee",
        {"user_id": senior_user},
        "name"
    )

    # If senior employee not found → fallback
    if not senior_emp:
        return default_search_link(*args, **kwargs)

    # Find employees who report to this senior
    employees = frappe.get_all(
        "Employee",
        filters={
            "status": "Active",
            "reports_to": senior_emp,
            "user_id": ["!=", None]
        },
        fields=["user_id"]
    )

    users = [e.user_id for e in employees]

    # Search text filter
    if txt:
        users = [u for u in users if txt.lower() in u.lower()]

    # Pagination
    users = users[start:start + page_len]

    # Return format expected by Assign dialog
    return [[u] for u in users]
