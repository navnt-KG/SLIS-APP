# import frappe


# def get_user_lab():
#     """
#     Returns the lab/district office name for the currently logged-in user
#     by looking up their Employee record.
#     Returns None if no employee record or lab found.
#     """
#     user = frappe.session.user

#     employee = frappe.db.get_value(
#         "Employee",
#         {"user_id": user},
#         ["employment_type", "custom_lab_name", "custom_district_office_name"],
#         as_dict=True
#     )

#     if not employee:
#         return None

#     if employee.employment_type == "District Office":
#         return employee.custom_district_office_name or None
#     else:
#         return employee.custom_lab_name or None


# @frappe.whitelist()
# def get_my_lab():
#     """
#     Returns the logged-in user's lab name and a display label.
#     Called by JS on page load to show which lab this dashboard is for.
#     """
#     lab = get_user_lab()
#     return {"lab": lab}


# @frappe.whitelist()
# def get_my_soil_intake_data(selected_year=None):
#     """
#     Same as get_soil_intake_data but automatically scoped to
#     the logged-in user's lab. No laboratory parameter needed.
#     """
#     if not selected_year:
#         return {"cards": {}, "table": []}

#     laboratory = get_user_lab()

#     if not laboratory:
#         return {"cards": {}, "table": [], "error": "no_lab"}

#     year_int   = int(selected_year)
#     curr_start = f"{year_int}-04-01"
#     curr_end   = f"{year_int + 1}-03-31"
#     prev_start = f"{year_int - 1}-04-01"
#     prev_end   = f"{year_int}-03-31"

#     lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"

#     sql = f"""
#         SELECT
#             COALESCE({lab_logic}, 'Unassigned') AS lab,

#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status NOT IN ('Draft', 'completed', 'Cancelled')
#                 THEN 1 ELSE 0
#             END) AS prev_pending,

#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 THEN 1 ELSE 0
#             END) AS received_this_year,

#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status = 'completed'
#                 THEN 1 ELSE 0
#             END) AS completed_this_year,

#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status NOT IN ('Draft', 'completed', 'Cancelled')
#                 THEN 1 ELSE 0
#             END) AS pending_this_year

#         FROM `tabSoil Sample Collection`
#         WHERE ({lab_logic}) = %s
#         GROUP BY {lab_logic}
#     """

#     params = (
#         [prev_start, prev_end]   +   # prev_pending
#         [curr_start, curr_end]   +   # received_this_year
#         [curr_start, curr_end]   +   # completed_this_year
#         [curr_start, curr_end]   +   # pending_this_year
#         [laboratory]                 # WHERE clause
#     )

#     rows = frappe.db.sql(sql, params, as_dict=True)

#     cards = {
#         "prev_year_balance":  0,
#         "received_this_year": 0,
#         "completed_tests":    0,
#         "cumulative_total":   0,
#         "pending_test":       0
#     }
#     table_data = []

#     for d in rows:
#         prev      = int(d.prev_pending       or 0)
#         received  = int(d.received_this_year  or 0)
#         completed = int(d.completed_this_year or 0)
#         pending   = int(d.pending_this_year   or 0)

#         table_data.append({
#             "lab":             d.lab or laboratory,
#             "prev_pending":    prev,
#             "received":        received,
#             "completed":       completed,
#             "current_pending": pending
#         })

#         cards["prev_year_balance"]  += prev
#         cards["received_this_year"] += received
#         cards["completed_tests"]    += completed
#         cards["pending_test"]       += pending

#     cards["cumulative_total"] = cards["prev_year_balance"] + cards["received_this_year"]

#     return {
#         "lab":   laboratory,
#         "cards": cards,
#         "table": table_data
#     }


# @frappe.whitelist()
# def get_my_filtered_sample_names(selected_year=None, card_type=None):
#     """
#     Returns list of record names for the logged-in user's lab
#     matching the given card type. Used by JS for navigation.
#     """
#     if not selected_year or not card_type:
#         return []

#     laboratory = get_user_lab()
#     if not laboratory:
#         return []

#     year_int   = int(selected_year)
#     curr_start = f"{year_int}-04-01"
#     curr_end   = f"{year_int + 1}-03-31"
#     prev_start = f"{year_int - 1}-04-01"
#     prev_end   = f"{year_int}-03-31"

#     lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"

#     if card_type == "prev_pending":
#         date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
#         date_params = [prev_start, prev_end]
#         status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
#     elif card_type == "received":
#         date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
#         date_params = [curr_start, curr_end]
#         status_cond = ""
#     elif card_type == "cumulative":
#         date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
#         date_params = [prev_start, curr_end]
#         status_cond = "AND status NOT IN ('Draft', 'Cancelled')"
#     elif card_type == "completed":
#         date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
#         date_params = [curr_start, curr_end]
#         status_cond = "AND status = 'completed'"
#     elif card_type == "pending":
#         date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
#         date_params = [curr_start, curr_end]
#         status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
#     else:
#         return []

#     sql = f"""
#         SELECT name
#         FROM `tabSoil Sample Collection`
#         WHERE {date_cond}
#         {status_cond}
#         AND ({lab_logic}) = %s
#     """

#     params = date_params + [laboratory]
#     rows   = frappe.db.sql(sql, params, as_dict=True)
#     return [r.name for r in rows]





import frappe

def get_user_lab():
    """
    Returns the lab/district office name for the currently logged-in user.
    """
    user = frappe.session.user
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        ["employment_type", "custom_lab_name", "custom_district_office_name"],
        as_dict=True
    )

    if not employee:
        return None

    if employee.employment_type == "District Office":
        return employee.custom_district_office_name or None
    else:
        return employee.custom_lab_name or None


@frappe.whitelist()
def get_my_lab():
    lab = get_user_lab()
    return {"lab": lab}


@frappe.whitelist()
def get_my_soil_intake_data(selected_year=None):
    if not selected_year:
        return {"cards": {}, "table": []}

    laboratory = get_user_lab()
    if not laboratory:
        return {"cards": {}, "table": [], "error": "no_lab"}

    year_int   = int(selected_year)
    curr_start = f"{year_int}-04-01"
    curr_end   = f"{year_int + 1}-03-31"
    prev_start = f"{year_int - 1}-04-01"
    prev_end   = f"{year_int}-03-31"

    lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"
    
    # Logic to use number_of_samples if > 0, otherwise count as 1
    sample_count = "COALESCE(NULLIF(number_of_samples, 0), 1)"

    sql = f"""
        SELECT
            COALESCE({lab_logic}, 'Unassigned') AS lab,

            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status NOT IN ('Draft', 'completed', 'Cancelled')
                THEN {sample_count} ELSE 0
            END) AS prev_pending,

            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                THEN {sample_count} ELSE 0
            END) AS received_this_year,

            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status = 'completed'
                THEN {sample_count} ELSE 0
            END) AS completed_this_year,

            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status NOT IN ('Draft', 'completed', 'Cancelled')
                THEN {sample_count} ELSE 0
            END) AS pending_this_year

        FROM `tabSoil Sample Collection`
        WHERE ({lab_logic}) = %s
        GROUP BY {lab_logic}
    """

    params = (
        [prev_start, prev_end]   + 
        [curr_start, curr_end]   + 
        [curr_start, curr_end]   + 
        [curr_start, curr_end]   + 
        [laboratory]
    )

    rows = frappe.db.sql(sql, params, as_dict=True)

    cards = {
        "prev_year_balance":  0,
        "received_this_year": 0,
        "completed_tests":    0,
        "cumulative_total":   0,
        "pending_test":       0
    }
    table_data = []

    for d in rows:
        prev      = int(d.prev_pending       or 0)
        received  = int(d.received_this_year  or 0)
        completed = int(d.completed_this_year or 0)
        pending   = int(d.pending_this_year   or 0)

        table_data.append({
            "lab":             d.lab or laboratory,
            "prev_pending":    prev,
            "received":        received,
            "completed":       completed,
            "current_pending": pending
        })

        cards["prev_year_balance"]  += prev
        cards["received_this_year"] += received
        cards["completed_tests"]    += completed
        cards["pending_test"]       += pending

    cards["cumulative_total"] = cards["prev_year_balance"] + cards["received_this_year"]

    return {
        "lab":   laboratory,
        "cards": cards,
        "table": table_data
    }


@frappe.whitelist()
def get_my_filtered_sample_names(selected_year=None, card_type=None):
    """
    Returns list of record names. Note: Navigation returns document IDs, 
    so sample_count weight is not needed here, only the filter logic.
    """
    if not selected_year or not card_type:
        return []

    laboratory = get_user_lab()
    if not laboratory:
        return []

    year_int   = int(selected_year)
    curr_start = f"{year_int}-04-01"
    curr_end   = f"{year_int + 1}-03-31"
    prev_start = f"{year_int - 1}-04-01"
    prev_end   = f"{year_int}-03-31"

    lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"

    if card_type == "prev_pending":
        date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [prev_start, prev_end]
        status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
    elif card_type == "received":
        date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = ""
    elif card_type == "cumulative":
        date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [prev_start, curr_end]
        status_cond = "AND status NOT IN ('Draft', 'Cancelled')"
    elif card_type == "completed":
        date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = "AND status = 'completed'"
    elif card_type == "pending":
        date_cond   = "assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
    else:
        return []

    sql = f"""
        SELECT name
        FROM `tabSoil Sample Collection`
        WHERE {date_cond}
        {status_cond}
        AND ({lab_logic}) = %s
    """

    params = date_params + [laboratory]
    rows   = frappe.db.sql(sql, params, as_dict=True)
    return [r.name for r in rows]