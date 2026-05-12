import frappe
import calendar
from datetime import date


def execute(filters=None):
    filters = filters or {}
    html = build_report(filters)
    return [], [], html


def get_ra_list():
    return frappe.get_list(
        "Employee",
        filters={
            "custom_soil_sample_tester": 1,
            "status": "Active"
        },
        fields=["name", "employee_name", "custom_lab_name"]
    )


def get_client_name(r):
    if r.client_type != "Department":
        return r.client_type
    return f"{r.type_of_collection} - {r.name_of_type}"


def build_report(filters):

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])

    fy_start = date(year, 4, 1) if month >= 4 else date(year - 1, 4, 1)
    fy_end = date(fy_start.year + 1, 3, 31)

    ra_list = get_ra_list()

    # 🔥 ONLY CURRENT FY DATA (MAIN FIX)
    records = frappe.get_all(
        "Soil Sample Collection",
        filters={
            "status": "completed",
            "completed_date": ["between", [fy_start, fy_end]]
        },
        fields=[
            "name", "client_type", "type_of_collection",
            "name_of_type", "completed_date", "total_parameter_count"
        ]
    )

    client_map = {}
    all_tests = set()

    # 🔥 BUILD STRUCTURE ONLY FROM FY DATA
    for r in records:

        if not r.completed_date:
            continue

        cname = get_client_name(r)

        use_total = 1

        if (
            r.client_type == "Department"
            and r.type_of_collection == "Scheme"
            and r.name_of_type
        ):
            use_total = frappe.db.get_value(
                "Department Programs Names",
                r.name_of_type,
                "count_the_total_parameter"
            ) or 0

        client_map[cname] = use_total

        if use_total == 0:
            tests = frappe.get_all(
                "Test Details",
                filters={"parent": r.name},
                fields=["test_name"]
            )
            for t in tests:
                if t.test_name:
                    all_tests.add(t.test_name)

    all_tests = list(all_tests)

    # 🔥 INIT DATA (even if empty structure)
    data = {}

    for ra in ra_list:
        data[ra.name] = {}
        for c in client_map:
            data[ra.name][c] = {
                "ss_dm": 0,
                "ss_pt": 0,
                "est_dm": 0,
                "est_pt": 0,
                "tests": {t: {"dm": 0, "pt": 0} for t in all_tests}
            }

    # 🔥 CALCULATION ONLY FY DATA
    for r in records:

        cname = get_client_name(r)

        todo_user = frappe.db.get_value(
            "ToDo",
            {
                "reference_type": "Soil Sample Collection",
                "reference_name": r.name
            },
            "allocated_to"
        )

        if not todo_user:
            continue

        ra_name = frappe.db.get_value(
            "Employee",
            {"user_id": todo_user},
            "name"
        )

        if not ra_name or cname not in data.get(ra_name, {}):
            continue

        prev = curr = 0

        if fy_start <= r.completed_date < month_start:
            prev = 1

        if month_start <= r.completed_date <= month_end:
            curr = 1

        data[ra_name][cname]["ss_dm"] += curr
        data[ra_name][cname]["ss_pt"] += (prev + curr)

        total = r.total_parameter_count or 0
        use_total = client_map[cname]

        if use_total == 1:

            if fy_start <= r.completed_date < month_start:
                prev = total
                curr = 0
            elif month_start <= r.completed_date <= month_end:
                prev = 0
                curr = total
            else:
                prev = curr = 0

            data[ra_name][cname]["est_dm"] += curr
            data[ra_name][cname]["est_pt"] += (prev + curr)

        else:

            tests = frappe.get_all(
                "Test Details",
                filters={"parent": r.name},
                fields=["test_name", "parameter_count"]
            )

            for t in tests:

                if fy_start <= r.completed_date < month_start:
                    prev = t.parameter_count or 0
                    curr = 0
                elif month_start <= r.completed_date <= month_end:
                    prev = 0
                    curr = t.parameter_count or 0
                else:
                    prev = curr = 0

                if t.test_name in data[ra_name][cname]["tests"]:
                    data[ra_name][cname]["tests"][t.test_name]["dm"] += curr
                    data[ra_name][cname]["tests"][t.test_name]["pt"] += (prev + curr)

    return generate_html(ra_list, client_map, all_tests, data)


# -----------------------------
# UI PART (UNCHANGED)
# -----------------------------
def generate_html(ra_list, client_map, all_tests, data):

    html = """
    <style>
    .report-container{
        width:100%;
        overflow-x:auto;
        overflow-y:auto;
        max-height:600px;
        border:1px solid #ccc;
    }

    .report-table{
        border-collapse:collapse;
        width:max-content;
        min-width:1400px;
        font-size:13px;
    }

    .report-table th{
        background:#f5f5f5;
        font-weight:600;
        position:sticky;
        top:0;
        z-index:2;
    }

    .report-table th,
    .report-table td{
        border:1px solid #ccc;
        padding:8px 14px;
        text-align:center;
        white-space:nowrap;
    }

    .ra-cell{
        background:#e3f2fd;
        font-weight:bold;
    }

    .total-cell{
        background:#f1f8e9;
        font-weight:bold;
    }
    </style>

    <div class="report-container">
    <table class="report-table">
    """

    html += "<tr><th rowspan='3'>Research Assistant</th><th rowspan='3'>Lab</th>"

    for c in client_map:
        if client_map[c] == 1:
            html += f"<th colspan='4'>{c}</th>"
        else:
            html += f"<th colspan='{2 + len(all_tests)*2}'>{c}</th>"

    html += "<th colspan='2'>SS TOTAL</th><th colspan='2'>EST TOTAL</th>"
    html += "</tr>"

    html += "<tr>"

    for c in client_map:
        html += "<th colspan='2'>SS</th>"

        if client_map[c] == 1:
            html += "<th colspan='2'>Estimate</th>"
        else:
            for t in all_tests:
                html += f"<th colspan='2'>{t} Estimate</th>"

    html += "<th colspan='4'></th>"
    html += "</tr>"

    html += "<tr>"

    for c in client_map:
        html += "<th>DM</th><th>PT</th>"

        if client_map[c] == 1:
            html += "<th>DM</th><th>PT</th>"
        else:
            for t in all_tests:
                html += "<th>DM</th><th>PT</th>"

    html += "<th>DM</th><th>PT</th><th>DM</th><th>PT</th>"
    html += "</tr>"

    for ra in ra_list:

        total_ss_dm = total_ss_pt = 0
        total_est_dm = total_est_pt = 0

        html += f"<tr><td class='ra-cell'>{ra.employee_name}</td><td>{ra.custom_lab_name or '-'}</td>"

        for c in client_map:

            row = data[ra.name][c]

            html += f"<td>{row['ss_dm']}</td><td>{row['ss_pt']}</td>"

            total_ss_dm += row['ss_dm']
            total_ss_pt += row['ss_pt']

            if client_map[c] == 1:
                html += f"<td>{row['est_dm']}</td><td>{row['est_pt']}</td>"

                total_est_dm += row['est_dm']
                total_est_pt += row['est_pt']

            else:
                for t in all_tests:
                    dm = row['tests'][t]['dm']
                    pt = row['tests'][t]['pt']

                    total_est_dm += dm
                    total_est_pt += pt

                    html += f"<td>{dm}</td><td>{pt}</td>"

        html += f"<td class='total-cell'>{total_ss_dm}</td><td class='total-cell'>{total_ss_pt}</td>"
        html += f"<td class='total-cell'>{total_est_dm}</td><td class='total-cell'>{total_est_pt}</td>"

        html += "</tr>"

    html += "</table></div>"
    return html