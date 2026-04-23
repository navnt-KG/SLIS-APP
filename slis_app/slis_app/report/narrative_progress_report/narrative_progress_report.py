import frappe
import calendar
from datetime import date

# ======================================================
# MAIN
# ======================================================
def execute(filters=None):

    filters = filters or {}

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    month_name = calendar.month_name[month]
    financial_year, fy_start, fy_end = get_financial_year_range(month, year)

    today = date.today()

    if date(year, month, 1) > today:
        return [], [], f"<h3>No data for {month_name} {year} (Future Month)</h3>"

    session1_columns = get_columns()
    session1_data = get_data(filters, month, year, financial_year, fy_start)

    user = frappe.session.user
    ra = is_ra(user)

    session2_raw = get_session_two_data(ra=ra, user=user)
    session2_columns = get_session_two_columns(session2_raw, ra=ra)
    session2_data = session2_raw["rows"]

    html = build_html(session1_columns, session1_data,
                      session2_columns, session2_data, ra=ra)

    message = f"Samples Analysed in {month_name} {financial_year}<br><br>{html}"

    return [], [], message


# ======================================================
# RA CHECK
# ======================================================
def is_ra(user):

    emp_name = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        "employee_name"
    )

    if not emp_name:
        return False

    return frappe.db.exists("ToDo", {
        "allocated_to": user,
        "custom_ra_employee_name": emp_name
    })


# ======================================================
# LAB LIST
# ======================================================
def get_labs(user):

    roles = frappe.get_roles(user)

    if user == "Administrator" or "System Manager" in roles:
        return frappe.get_all("Soil Laboratory", pluck="name")

    if "Senior Chemist" in roles:
        lab = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "custom_lab_name"
        )
        return [lab] if lab else []

    return frappe.get_all("Soil Laboratory", pluck="name")


# ======================================================
# LAB MAPPING
# ======================================================
def get_sample_lab(s):
    return s.target_lab if s.client_type == "Department" else s.lab_name


# ======================================================
# FINANCIAL YEAR
# ======================================================
def get_financial_year_range(month, year):

    if month >= 4:
        return f"{year}-{year+1}", date(year, 4, 1), date(year+1, 3, 31)
    else:
        return f"{year-1}-{year}", date(year-1, 4, 1), date(year, 3, 31)


def get_month_end_date(month, year):
    return date(year, month, calendar.monthrange(year, month)[1])


# ======================================================
# SESSION 1
# ======================================================
def get_columns():
    return [
        {"label": "Name", "fieldname": "name"},
        {"label": "Profile Target", "fieldname": "profile_target"},
        {"label": "Other Target", "fieldname": "other_target"},
        {"label": "Total Target", "fieldname": "target"},
        {"label": "DM", "fieldname": "dm"},
        {"label": "PT", "fieldname": "pt"},
        {"label": "Pending", "fieldname": "pending"},
    ]


def get_data(filters, month, year, financial_year, fy_start):

    user = frappe.session.user
    month_start = date(year, month, 1)
    month_end = get_month_end_date(month, year)

    if is_ra(user):

        emp = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            ["employee_name"],
            as_dict=True
        )

        target = frappe.db.get_value(
            "Monthly Target",
            {"financial_year": financial_year},
            ["profile_sample_count", "other_sample_count"],
            as_dict=True
        )

        profile = target.profile_sample_count if target else 0
        other = target.other_sample_count if target else 0

        samples = frappe.db.sql("""
            SELECT s.status, s.completed_date
            FROM `tabSoil Sample Collection` s
            INNER JOIN `tabToDo` t ON t.reference_name = s.name
            WHERE t.allocated_to=%s
        """, user, as_dict=True)

        dm = pt = pending = 0

        for s in samples:

            if s.status == "completed" and s.completed_date:

                if month_start <= s.completed_date <= month_end:
                    dm += 1

                if fy_start <= s.completed_date <= month_end:
                    pt += 1

            elif s.status == "With Research Assistant":
                pending += 1

        return [{
            "name": emp.employee_name if emp else user,
            "profile_target": profile,
            "other_target": other,
            "target": profile + other,
            "dm": dm,
            "pt": pt,
            "pending": pending
        }]

    labs = get_labs(user)

    samples = frappe.get_all(
        "Soil Sample Collection",
        fields=["lab_name", "target_lab", "client_type",
                "status", "completed_date"]
    )

    data = []

    for lab in labs:

        dm = pt = pending = 0

        for s in samples:

            sample_lab = get_sample_lab(s)

            if sample_lab != lab:
                continue

            if s.status == "completed" and s.completed_date:

                if month_start <= s.completed_date <= month_end:
                    dm += 1

                if fy_start <= s.completed_date <= month_end:
                    pt += 1

            elif s.status in (
                "With Senior Chemist",
                "With Research Assistant",
                "Returned to Senior Chemist(Overload)"
            ):
                pending += 1

        target = frappe.db.sql("""
            SELECT 
                SUM(mt.profile_sample_count * lt.ra_count) as profile,
                SUM(mt.other_sample_count * lt.ra_count) as other
            FROM `tabMonthly Target` mt
            INNER JOIN `tabLab Target` lt ON lt.parent = mt.name
            WHERE lt.lab_name=%s
            AND mt.financial_year=%s
        """, (lab, financial_year), as_dict=True)

        profile = target[0]["profile"] or 0
        other = target[0]["other"] or 0

        data.append({
            "name": lab,
            "profile_target": profile,
            "other_target": other,
            "target": profile + other,
            "dm": dm,
            "pt": pt,
            "pending": pending
        })

    return data


# ======================================================
# SESSION 2 COLUMNS
# ======================================================
def get_session_two_columns(data, ra=False):

    # First column label: "Name" for RA, "Lab" for others
    first_col_label = "Name" if ra else "Lab"

    cols = [{"label": first_col_label, "fieldname": "lab_name"}]

    for c in data["clients"]:
        cols.append({"label": c, "fieldname": c})

    cols.append({"label": "Total Pending", "fieldname": "total_pending"})

    return cols


# ======================================================
# SESSION 2 DATA
# ======================================================
def get_session_two_data(ra=False, user=None):

    if user is None:
        user = frappe.session.user

    # ── RA: only samples assigned to this RA via ToDo ──
    if ra:

        emp_name = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "employee_name"
        )

        # Fetch all sample names assigned to this RA
        assigned_samples = frappe.db.sql("""
            SELECT t.reference_name
            FROM `tabToDo` t
            WHERE t.allocated_to = %s
              AND t.custom_ra_employee_name = %s
        """, (user, emp_name), as_dict=True)

        assigned_names = [r.reference_name for r in assigned_samples]

        if not assigned_names:
            return {"rows": [], "clients": []}

        samples = frappe.get_all(
            "Soil Sample Collection",
            filters={"name": ["in", assigned_names]},
            fields=[
                "name",
                "lab_name",
                "target_lab",
                "client_type",
                "type_of_collection",
                "name_of_type",
                "status"
            ]
        )

        def get_client_names(r):

            if r.client_type == "Department":

                type_col = str(r.get("type_of_collection") or "").strip()
                name_type = str(r.get("name_of_type") or "").strip()

                if type_col and name_type:
                    base_name = f"{type_col} - {name_type}"
                elif name_type:
                    base_name = name_type
                elif type_col:
                    base_name = type_col
                else:
                    base_name = "Department"

                test_items = frappe.get_all(
                    "Scheme Test List",
                    filters={"parent": r.name_of_type},
                    fields=["test_item"]
                )

                names = []

                for t in test_items:
                    if t.test_item:
                        names.append(f"{base_name} - {t.test_item}")

                return names if names else [base_name]

            return [r.client_type]

        clients = set()
        ra_row = {}

        for r in samples:

            if r.status == "completed":
                continue

            if r.status not in (
                "With Research Assistant",
            ):
                continue

            cnames = get_client_names(r)

            for cname in cnames:
                clients.add(cname)
                ra_row[cname] = ra_row.get(cname, 0) + 1

        total = sum(ra_row.values())
        ra_row["lab_name"] = emp_name or user
        ra_row["total_pending"] = total

        return {"rows": [ra_row], "clients": list(clients)}

    # ── Non-RA: original lab-based logic ──
    labs = get_labs(user)

    samples = frappe.get_all(
        "Soil Sample Collection",
        fields=[
            "name",
            "lab_name",
            "target_lab",
            "client_type",
            "type_of_collection",
            "name_of_type",
            "status"
        ]
    )

    def get_client_names(r):

        if r.client_type == "Department":

            type_col = str(r.get("type_of_collection") or "").strip()
            name_type = str(r.get("name_of_type") or "").strip()

            if type_col and name_type:
                base_name = f"{type_col} - {name_type}"
            elif name_type:
                base_name = name_type
            elif type_col:
                base_name = type_col
            else:
                base_name = "Department"

            test_items = frappe.get_all(
                "Scheme Test List",
                filters={"parent": r.name_of_type},
                fields=["test_item"]
            )

            names = []

            for t in test_items:
                if t.test_item:
                    names.append(f"{base_name} - {t.test_item}")

            return names if names else [base_name]

        return [r.client_type]

    data = {}
    clients = set()

    for lab in labs:
        data[lab] = {}

    for r in samples:

        sample_lab = get_sample_lab(r)

        if sample_lab not in data:
            continue
        if r.status == "completed":
            continue

        if r.status not in (
            "With Senior Chemist",
            "With Research Assistant",
            "Returned to Senior Chemist(Overload)"
        ):
            continue

        cnames = get_client_names(r)

        for cname in cnames:
            clients.add(cname)
            data[sample_lab][cname] = data[sample_lab].get(cname, 0) + 1

    result = []

    for name in data:

        row = {"lab_name": name}
        total = 0

        for c in clients:
            val = data[name].get(c, 0)
            row[c] = val
            total += val

        row["total_pending"] = total
        result.append(row)

    return {"rows": result, "clients": list(clients)}


# ======================================================
# HTML
# ======================================================
def build_html(c1, d1, c2, d2, ra=False):

    html = """
    <style>
    .box{overflow-x:auto;border:1px solid #ccc;margin-bottom:20px;}
    table{border-collapse:collapse;width:100%;}
    th,td{border:1px solid #ccc;padding:8px;text-align:center;}
    th{background:#f5f5f5;}
    </style>
    """

    # Session 1
    html += "<h3>Narrative Progress Report</h3><div class='box'><table><tr>"
    for col in c1:
        html += f"<th>{col['label']}</th>"
    html += "</tr>"

    for row in d1:
        html += "<tr>"
        for col in c1:
            html += f"<td>{row.get(col['fieldname'], '')}</td>"
        html += "</tr>"

    html += "</table></div>"

    # Session 2 — first column heading comes from c2
    first_col_label = c2[0]["label"] if c2 else ("Name" if ra else "Lab")

    html += "<h3>Pending Work</h3><div class='box'><table>"

    main_headers = {}
    field_map = {}

    for col in c2:
        fname = col["fieldname"]
        label = col["label"]

        if fname in ("lab_name", "total_pending"):
            continue

        parts = label.split(" - ")

        if len(parts) >= 3:
            main = " - ".join(parts[:2])
            sub = parts[2]
        else:
            main = label
            sub = ""

        if main not in main_headers:
            main_headers[main] = []

        main_headers[main].append(sub)
        field_map[(main, sub)] = fname

    order = ["Profile", "Surface"]

    for main in main_headers:
        main_headers[main] = sorted(
            main_headers[main],
            key=lambda x: order.index(x) if x in order else 99
        )

    html += f"<tr><th rowspan='2'>{first_col_label}</th>"

    for main in main_headers:
        html += f"<th colspan='{len(main_headers[main])}'>{main}</th>"

    html += "<th rowspan='2'>Total Pending</th></tr>"

    html += "<tr>"

    for main in main_headers:
        for sub in main_headers[main]:
            html += f"<th>{sub}</th>"

    html += "</tr>"

    for row in d2:
        html += "<tr>"

        html += f"<td>{row.get('lab_name', '')}</td>"

        for main in main_headers:
            for sub in main_headers[main]:
                fname = field_map.get((main, sub))
                html += f"<td>{row.get(fname, 0)}</td>"

        html += f"<td>{row.get('total_pending', 0)}</td>"

        html += "</tr>"

    html += "</table></div>"

    return html