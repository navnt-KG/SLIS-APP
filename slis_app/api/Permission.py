import frappe

def sample_permission_query(user=None):
    user = user or frappe.session.user
    roles = frappe.get_roles(user)

    # ADMIN / MD - Full access
    if user == "Administrator" or "slis_admin" in roles:
        return ""

    # Employee details fetch cheyyunnu
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        ["employment_type", "custom_lab_name", "custom_district_office_name"],
        as_dict=True
    )

    if not employee:
        return f"`tabSoil Sample Collection`.owner = '{user}'"

    conditions = []

    # =====================================================
    # SOIL INTAKER L1 / SOIL TESTER L1
    # ONLY OWN CREATED + ASSIGNED SAMPLES
    # =====================================================
    if "Soil Intaker L1" in roles or "Soil Tester L1" in roles:
        return (
            f"(`tabSoil Sample Collection`.owner = '{user}' "
            f"OR `tabSoil Sample Collection`.`_assign` LIKE '%%\"{user}\"%%')"
        )

    # =====================================================
    # SOIL INTAKER L3
    # ONLY ASSIGNED SAMPLES
    # =====================================================
    if "Soil Intaker L3" in roles:
        return (
            f"(`tabSoil Sample Collection`.`_assign` LIKE '%%\"{user}\"%%')"
        )

    # DISTRICT OFFICE
    if employee.employment_type == "District Office":
        conditions.append("(client_type = 'Department')")

    # BASIC PERMISSIONS
    conditions.append(
        f"`tabSoil Sample Collection`.owner = '{user}'"
    )

    conditions.append(
        f"(`tabSoil Sample Collection`.`_assign` LIKE '%%\"{user}\"%%')"
    )

    # PSC OFFICER
    if "slis_admin" in roles or "PSC Officer" in roles:
        conditions.append(
            "("
            "employee_type = 'Lab' "
            "OR (client_type = 'Department' "
            "AND status IN ('With PSC Officer', 'Returned to PSC Officer (Overload)'))"
            ")"
        )

    # ASSISTANT DIRECTOR
    if "Soil Intaker L2" in roles and employee.custom_district_office_name:
        conditions.append(
            f"(employee_type = 'District Office' "
            f"AND district_office_name = '{employee.custom_district_office_name}')"
        )

    # SENIOR CHEMIST
    if "Soil Intaker L2" in roles and employee.custom_lab_name:
        conditions.append(
            f"(client_type = 'Department' "
            f"AND target_lab = '{employee.custom_lab_name}' "
            f"AND status IN ("
            f"'With Senior Chemist', "

            f"'With Research Assistant', "
            f"'Transferred', "
            f"'Returned', "
            f"'completed', "
            f"'cancelled'"
            f"))"
        )

    # FARMER / CONSULTANCY
    if employee.custom_lab_name and employee.employment_type != "District Office":
        conditions.append(
            f"(client_type IN ('Farmer', 'Consultancy') "
            f"AND lab_name = '{employee.custom_lab_name}')"
        )

    if conditions:
        return f"({' OR '.join(set(conditions))})"

    return ""