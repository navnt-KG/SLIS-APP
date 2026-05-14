# import frappe

# @frappe.whitelist()
# def get_soil_intake_data(selected_year=None, laboratory=None):

#     if not selected_year:
#         return {"cards": {}, "table": []}

#     year_int   = int(selected_year)
#     curr_start = f"{year_int}-04-01"
#     curr_end   = f"{year_int + 1}-03-31"
#     prev_start = f"{year_int - 1}-04-01"
#     prev_end   = f"{year_int}-03-31"

#     # Lab logic: if lab_name is filled use it, else use target_lab
#     lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"

#     # Build lab filter
#     lab_condition = ""
#     lab_params    = []
#     if laboratory and laboratory not in ("", "All Laboratories"):
#         lab_condition = f"AND {lab_logic} = %s"
#         lab_params    = [laboratory]

#     sql = f"""
#         SELECT
#             COALESCE({lab_logic}, 'Unassigned') AS lab,

#             -- PREV YEAR BALANCE
#             -- assigned_to_lab_date in PREV FY range
#             -- status NOT IN (Draft, Completed, Cancelled)
#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status NOT IN ('Draft', 'completed', 'Cancelled')
#                 THEN 1 ELSE 0
#             END) AS prev_pending,

#             -- RECEIVED THIS YEAR
#             -- assigned_to_lab_date in CURR FY range (all statuses)
#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 THEN 1 ELSE 0
#             END) AS received_this_year,

#             -- COMPLETED THIS YEAR
#             -- assigned_to_lab_date in CURR FY, status = completed
#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status = 'completed'
#                 THEN 1 ELSE 0
#             END) AS completed_this_year,

#             -- PENDING THIS YEAR
#             -- assigned_to_lab_date in CURR FY
#             -- status NOT IN (Draft, Completed, Cancelled)
#             SUM(CASE
#                 WHEN assigned_to_lab_date BETWEEN %s AND %s
#                 AND  status NOT IN ('Draft', 'completed', 'Cancelled')
#                 THEN 1 ELSE 0
#             END) AS pending_this_year

#         FROM `tabSoil Sample Collection`
#         WHERE 1=1 {lab_condition}
#         GROUP BY {lab_logic}
#         ORDER BY lab ASC
#     """

#     params = (
#         [prev_start, prev_end]   +   # prev_pending
#         [curr_start, curr_end]   +   # received_this_year
#         [curr_start, curr_end]   +   # completed_this_year
#         [curr_start, curr_end]   +   # pending_this_year
#         lab_params
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
#         prev      = int(d.prev_pending      or 0)
#         received  = int(d.received_this_year or 0)
#         completed = int(d.completed_this_year or 0)
#         pending   = int(d.pending_this_year  or 0)

#         table_data.append({
#             "lab":             d.lab or "Unassigned",
#             "prev_pending":    prev,
#             "received":        received,
#             "completed":       completed,
#             "current_pending": pending
#         })

#         cards["prev_year_balance"]  += prev
#         cards["received_this_year"] += received
#         cards["completed_tests"]    += completed
#         cards["pending_test"]       += pending

#     # Cumulative = prev year balance + received this year
#     cards["cumulative_total"] = cards["prev_year_balance"] + cards["received_this_year"]

#     return {"cards": cards, "table": table_data}







import frappe

@frappe.whitelist()
def get_soil_intake_data(selected_year=None, laboratory=None):

    if not selected_year:
        return {"cards": {}, "table": []}

    year_int   = int(selected_year)
    curr_start = f"{year_int}-04-01"
    curr_end   = f"{year_int + 1}-03-31"
    prev_start = f"{year_int - 1}-04-01"
    prev_end   = f"{year_int}-03-31"

    # Lab logic: if lab_name is filled use it, else use target_lab
    lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"
    
    # Sample Count logic: Use number_of_samples field if it has a value > 0, else default to 1
    sample_count = "COALESCE(NULLIF(number_of_samples, 0), 1)"

    # Build lab filter
    lab_condition = ""
    lab_params    = []
    if laboratory and laboratory not in ("", "All Laboratories"):
        lab_condition = f"AND {lab_logic} = %s"
        lab_params    = [laboratory]

    sql = f"""
        SELECT
            COALESCE({lab_logic}, 'Unassigned') AS lab,

            -- PREV YEAR BALANCE (Weighted by number_of_samples)
            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status NOT IN ('Draft', 'completed', 'Cancelled')
                THEN {sample_count} ELSE 0
            END) AS prev_pending,

            -- RECEIVED THIS YEAR (Weighted by number_of_samples)
            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                THEN {sample_count} ELSE 0
            END) AS received_this_year,

            -- COMPLETED THIS YEAR (Weighted by number_of_samples)
            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status = 'completed'
                THEN {sample_count} ELSE 0
            END) AS completed_this_year,

            -- PENDING THIS YEAR (Weighted by number_of_samples)
            SUM(CASE
                WHEN assigned_to_lab_date BETWEEN %s AND %s
                AND  status NOT IN ('Draft', 'completed', 'Cancelled')
                THEN {sample_count} ELSE 0
            END) AS pending_this_year

        FROM `tabSoil Sample Collection`
        WHERE 1=1 {lab_condition}
        GROUP BY {lab_logic}
        ORDER BY lab ASC
    """

    params = (
        [prev_start, prev_end]   +   # prev_pending
        [curr_start, curr_end]   +   # received_this_year
        [curr_start, curr_end]   +   # completed_this_year
        [curr_start, curr_end]   +   # pending_this_year
        lab_params
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
        prev      = int(d.prev_pending      or 0)
        received  = int(d.received_this_year or 0)
        completed = int(d.completed_this_year or 0)
        pending   = int(d.pending_this_year  or 0)

        table_data.append({
            "lab":             d.lab or "Unassigned",
            "prev_pending":    prev,
            "received":        received,
            "completed":       completed,
            "current_pending": pending
        })

        cards["prev_year_balance"]  += prev
        cards["received_this_year"] += received
        cards["completed_tests"]    += completed
        cards["pending_test"]       += pending

    # Cumulative = prev year balance + received this year
    cards["cumulative_total"] = cards["prev_year_balance"] + cards["received_this_year"]

    return {"cards": cards, "table": table_data}


@frappe.whitelist()
def get_filtered_sample_names(selected_year=None, laboratory=None, card_type=None):
    """
    Returns list of record names matching the card filters.
    Used by JS to navigate: name in [ids]
    """
    if not selected_year or not card_type:
        return []

    year_int   = int(selected_year)
    curr_start = f"{year_int}-04-01"
    curr_end   = f"{year_int + 1}-03-31"
    prev_start = f"{year_int - 1}-04-01"
    prev_end   = f"{year_int}-03-31"

    lab_logic = "COALESCE(NULLIF(lab_name, ''), target_lab)"

    # Date condition
    if card_type == "prev_pending":
        date_cond = f"assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [prev_start, prev_end]
        status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
    elif card_type == "received":
        date_cond = f"assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = ""
    elif card_type == "cumulative":
        date_cond = f"assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [prev_start, curr_end]
        status_cond = "AND status NOT IN ('Draft', 'Cancelled')"
    elif card_type == "completed":
        date_cond = f"assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = "AND status = 'completed'"
    elif card_type == "pending":
        date_cond = f"assigned_to_lab_date BETWEEN %s AND %s"
        date_params = [curr_start, curr_end]
        status_cond = "AND status NOT IN ('Draft', 'completed', 'Cancelled')"
    else:
        return []

    lab_condition = ""
    lab_params = []
    if laboratory and laboratory not in ("", "All Laboratories"):
        lab_condition = f"AND ({lab_logic}) = %s"
        lab_params = [laboratory]

    sql = f"""
        SELECT name
        FROM `tabSoil Sample Collection`
        WHERE {date_cond}
        {status_cond}
        {lab_condition}
    """

    params = date_params + lab_params
    rows = frappe.db.sql(sql, params, as_dict=True)
    return [r.name for r in rows]