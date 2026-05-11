import frappe
from frappe import _


def build_date_range(selected_year, selected_month):
    """
    Returns (start_date, end_date) based on FY and optional month.
    FY runs April to March.
    If month is given, scope to that calendar month within the FY.
    """
    year_int = int(selected_year)

    if selected_month:
        month_int = int(selected_month)
        # Months 4-12 belong to the start year; 1-3 belong to the next year
        if month_int >= 4:
            start = f"{year_int}-{month_int:02d}-01"
        else:
            start = f"{year_int + 1}-{month_int:02d}-01"

        # Last day of month
        import calendar
        actual_year = year_int if month_int >= 4 else year_int + 1
        last_day    = calendar.monthrange(actual_year, month_int)[1]
        end         = f"{actual_year}-{month_int:02d}-{last_day:02d}"
    else:
        # Full FY
        start = f"{year_int}-04-01"
        end   = f"{year_int + 1}-03-31"

    return start, end


def build_lab_condition(laboratory, field_expr):
    """
    Returns (condition_sql, params) for lab filtering.
    field_expr is the SQL expression for the lab column.
    """
    if laboratory and laboratory not in ("", "All Laboratories"):
        return f"AND ({field_expr}) = %s", [laboratory]
    return "", []


# ======================================================
# SAMPLE STATUS CHART
# Group by status from Soil Sample Collection
# ======================================================

@frappe.whitelist()
def get_sample_status_data(selected_year=None, selected_month=None, laboratory=None):
    if not selected_year:
        return {"labels": [], "datasets": []}

    start, end = build_date_range(selected_year, selected_month)
    lab_logic   = "COALESCE(NULLIF(lab_name, ''), target_lab)"
    lab_cond, lab_params = build_lab_condition(laboratory, lab_logic)

    sql = f"""
        SELECT
            status,
            COUNT(*) AS count
        FROM `tabSoil Sample Collection`
        WHERE assigned_to_lab_date BETWEEN %s AND %s
        {lab_cond}
        GROUP BY status
        ORDER BY count DESC
    """

    params = [start, end] + lab_params
    rows   = frappe.db.sql(sql, params, as_dict=True)

    labels = [r.status for r in rows]
    values = [int(r.count) for r in rows]

    return {
        "labels":   labels,
        "datasets": [{"name": "Samples", "values": values}]
    }


# ======================================================
# EMPLOYEE WISE WORK STATUS CHART
# From ToDo, filtered by lab via Soil Sample Collection join
# ======================================================

@frappe.whitelist()
def get_employee_status_data(selected_year=None, selected_month=None, laboratory=None):
    if not selected_year:
        return {"labels": [], "datasets": []}

    start, end = build_date_range(selected_year, selected_month)
    lab_logic   = "COALESCE(NULLIF(ssc.lab_name, ''), ssc.target_lab)"
    lab_cond, lab_params = build_lab_condition(laboratory, lab_logic)

    sql = f"""
        SELECT
            t.custom_ra_employee_name AS employee,
            t.status
        FROM `tabToDo` t
        INNER JOIN `tabSoil Sample Collection` ssc
            ON ssc.name = t.reference_name
        WHERE t.reference_type = 'Soil Sample Collection'
          AND t.custom_ra_employee_name IS NOT NULL
          AND t.custom_ra_employee_name != ''
          AND ssc.assigned_to_lab_date BETWEEN %s AND %s
          {lab_cond}
    """

    params = [start, end] + lab_params
    rows   = frappe.db.sql(sql, params, as_dict=True)

    employees     = sorted(list(set([r.employee for r in rows if r.employee])))
    completed_vals = []
    pending_vals   = []
    cancelled_vals = []

    for emp in employees:
        emp_tasks = [r for r in rows if r.employee == emp]
        completed_vals.append(len([t for t in emp_tasks if t.status == "Closed"]))
        pending_vals.append(len([t for t in emp_tasks if t.status not in ["Closed", "Cancelled"]]))
        cancelled_vals.append(len([t for t in emp_tasks if t.status == "Cancelled"]))

    return {
        "labels": employees,
        "datasets": [
            {"name": _("Completed"), "values": completed_vals},
            {"name": _("Pending"),   "values": pending_vals},
            {"name": _("Cancelled"), "values": cancelled_vals}
        ]
    }


# ======================================================
# SCHEME-WISE TOTAL SAMPLES CHART
# From Clients doctype, filtered by lab via Soil Sample Collection
# ======================================================

@frappe.whitelist()
def get_scheme_data(selected_year=None, selected_month=None, laboratory=None):
    if not selected_year:
        return {"labels": [], "datasets": []}

    start, end = build_date_range(selected_year, selected_month)
    lab_logic   = "COALESCE(NULLIF(ssc.lab_name, ''), ssc.target_lab)"
    lab_cond, lab_params = build_lab_condition(laboratory, lab_logic)

    sql = f"""
        SELECT
            c.type_of_collection AS scheme,
            COUNT(ssc.name) AS count
        FROM `tabSoil Sample Collection` ssc
        INNER JOIN `tabClients` c
            ON c.name = ssc.client
        WHERE c.client_type    = 'Department'
          AND c.type_of_collection = 'Scheme'
          AND ssc.assigned_to_lab_date BETWEEN %s AND %s
          {lab_cond}
        GROUP BY c.type_of_collection
        ORDER BY count DESC
    """

    params = [start, end] + lab_params
    rows   = frappe.db.sql(sql, params, as_dict=True)

    # If grouping by type_of_collection gives one row, try grouping by client name instead
    # to show individual scheme clients
    if len(rows) <= 1:
        sql2 = f"""
            SELECT
                c.client_name AS scheme,
                COUNT(ssc.name) AS count
            FROM `tabSoil Sample Collection` ssc
            INNER JOIN `tabClients` c
                ON c.name = ssc.client
            WHERE c.client_type       = 'Department'
              AND c.type_of_collection = 'Scheme'
              AND ssc.assigned_to_lab_date BETWEEN %s AND %s
              {lab_cond}
            GROUP BY c.client_name
            ORDER BY count DESC
        """
        rows = frappe.db.sql(sql2, params, as_dict=True)

    labels = [r.scheme for r in rows]
    values = [int(r.count) for r in rows]

    return {
        "labels":   labels,
        "datasets": [{"name": "Samples", "values": values}]
    }