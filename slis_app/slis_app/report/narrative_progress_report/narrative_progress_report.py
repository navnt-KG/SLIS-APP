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

    session2_raw = get_session_two_data()
    session2_columns = get_session_two_columns(session2_raw)
    session2_data = session2_raw["rows"]

    html = build_html(session1_columns, session1_data,
                      session2_columns, session2_data)

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
# SESSION 1 (UNCHANGED)
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
# 🔥 UPDATED PENDING
# ======================================================
def get_session_two_columns(data):

    cols = [{"label": "Lab", "fieldname": "lab_name"}]

    for c in data["clients"]:
        cols.append({"label": c, "fieldname": c})

    cols.append({"label": "Total Pending", "fieldname": "total_pending"})

    return cols


def get_session_two_data():

    user = frappe.session.user
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

    # ✅ FINAL FIXED FUNCTION
    def get_client_name(r):

        if r.client_type == "Department":

            type_col = str(r.get("type_of_collection") or "").strip()
            name_type = str(r.get("name_of_type") or "").strip()

            if type_col and name_type:
                return f"{type_col} - {name_type}"

            if name_type:
                return name_type

            if type_col:
                return type_col

            return "Department"

        return r.client_type

    data = {}
    clients = set()

    if is_ra(user):

        records = frappe.db.sql("""
            SELECT s.*
            FROM `tabSoil Sample Collection` s
            INNER JOIN `tabToDo` t ON t.reference_name = s.name
            WHERE t.allocated_to=%s
        """, user, as_dict=True)

        emp_name = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "employee_name"
        )

        data[emp_name] = {}

        for r in records:

            if r.status != "With Research Assistant":
                continue

            cname = get_client_name(r)
            clients.add(cname)

            data[emp_name][cname] = data[emp_name].get(cname, 0) + 1

    else:

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

            cname = get_client_name(r)
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
def build_html(c1, d1, c2, d2):

    html = """
    <style>
    .box{overflow-x:auto;border:1px solid #ccc;margin-bottom:20px;}
    table{border-collapse:collapse;width:100%;}
    th,td{border:1px solid #ccc;padding:8px;text-align:center;}
    th{background:#f5f5f5;}
    </style>
    """

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

    html += "<h3>Pending Work</h3><div class='box'><table><tr>"

    for col in c2:
        html += f"<th>{col['label']}</th>"

    html += "</tr>"

    for row in d2:
        html += "<tr>"
        for col in c2:
            html += f"<td>{row.get(col['fieldname'], 0)}</td>"
        html += "</tr>"

    html += "</table></div>"

    return html