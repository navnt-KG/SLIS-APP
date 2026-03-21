# # Copyright (c) 2026, navaneeth and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.model.naming import make_autoname

# class Clients(Document):

#     def autoname(self):
#         # 1. Administrator Bypass
#         if frappe.session.user == "Administrator":
#             self.name = make_autoname("ADM-CLT-.#####")
#             return

#         # 2. Existing Validations
#         if not self.client_type:
#             frappe.throw("Client Type is required")

#         # 3. Fetch Lab Name and Write to Document
#         user_full_lab_name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "custom_lab_name")
        
#         if not user_full_lab_name:
#             frappe.throw(f"User {frappe.session.user} is not linked to an Employee record with a Lab assigned.")
        
#         # Storing the full lab name in the field you created
#         self.lab_name = user_full_lab_name

#         # 4. Lab Abbreviation Mapping
#         lab_abbreviation_map = {
#             "Hi-Tech Soil Analytical Lab WYD": "WYD",
#             "Regional Soil Analytical Laboratory Alappuzha": "ALP",
#             "Regional Soil Analytical Laboratory Kozhikode": "KZK",
#             "Regional Soil Analytical Laboratory Thrissur": "TSR",
#             "Soil and Plant Health Clinic, Kasaragod": "KSD",
#             "Soil and Plant Health Clinic, Pathanamthitta": "PTA",
#             "Central Soil Analytical Lab, Parottukonam": "TVM"
#         }

#         lab_code = lab_abbreviation_map.get(self.lab_name)
#         if not lab_code:
#             frappe.throw(f"Naming prefix not found for lab: {self.lab_name}")

#         # 5. Client Type Prefix Mapping
#         prefix_map = {
#             "Farmer": "CL-FS",
#             "Department": "CL-DS",
#             "Consultancy": "CL-CS"
#         }

#         prefix = prefix_map.get(self.client_type)
#         if not prefix:
#             frappe.throw("Invalid Client Type")

#         # 6. Generate Final Name
#         # Format: CL-FS-ALP-.#####
#         self.name = make_autoname(f"{prefix}-{lab_code}-.#####")




import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Clients(Document):

    def autoname(self):
        # 1. Administrator Bypass
        if frappe.session.user == "Administrator":
            self.name = make_autoname("ADM-CLT-.#####")
            return

        # 2. Existing Validations
        if not self.client_type:
            frappe.throw("Client Type is required")

        # 3. Define Mappings
        lab_map = {
            "Hi-Tech Soil Analytical Lab WYD": "WYD",
            "Regional Soil Analytical Laboratory Alappuzha": "ALP",
            "Regional Soil Analytical Laboratory Kozhikode": "KZK",
            "Regional Soil Analytical Laboratory Thrissur": "TSR",
            "Soil and Plant Health Clinic, Kasaragod": "KSD",
            "Soil and Plant Health Clinic, Pathanamthitta": "PTA",
            "Central Soil Analytical Lab, Parottukonam": "TVM"
        }

        district_map = {
            "Trivandrum": "TVC", "Kollam": "QLN", "Pathanamthitta": "PTA",
            "Alappuzha": "ALP", "Kottayam": "KTM", "Idukki": "IDU",
            "Ernakulam": "ERS", "Thrissur": "TSR", "Palakkad": "PGT",
            "Malappuram": "MLP", "Kozhikode": "KZK", "Wayanad": "WAY",
            "Kannur": "CAN", "Kasaragod": "KGQ"
        }

        # 4. Fetch Employee Data
        employee = frappe.db.get_value(
            "Employee", 
            {"user_id": frappe.session.user}, 
            ["custom_lab_name", "custom_district_office_name"], 
            as_dict=True
        )
        
        if not employee:
            frappe.throw(f"User {frappe.session.user} is not linked to an Employee record.")

        # 5. Determine Lab/District Code
        lab_code = None
        final_office_name = None

        # Try Lab first
        if employee.custom_lab_name:
            lab_code = lab_map.get(employee.custom_lab_name)
            final_office_name = employee.custom_lab_name
        
        # Fallback to District Office
        if not lab_code and employee.custom_district_office_name:
            lab_code = district_map.get(employee.custom_district_office_name)
            final_office_name = employee.custom_district_office_name

        if not lab_code:
            frappe.throw("Neither a valid Lab nor a District Office was found for your Employee record.")

        # Store the office name in the document field
        self.lab_name = final_office_name

        # 6. Client Type Prefix Mapping
        prefix_map = {
            "Farmer": "CL-FS",
            "Department": "CL-DS",
            "Consultancy": "CL-CS"
        }

        prefix = prefix_map.get(self.client_type)
        if not prefix:
            frappe.throw("Invalid Client Type")

        # 7. Generate Final Name
        # Format: CL-FS-ALP-.#####
        self.name = make_autoname(f"{prefix}-{lab_code}-.#####")




#user permision to only see the clients created by their lab or district office

import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    # Allow Administrator full access
    if user == "Administrator":
        return ""

    lab = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        "custom_lab_name"
    )

    if lab:
        return f"`tabClients`.`login_lab_name` = '{lab}'"

    return "1=0"


def has_permission(doc, user=None):
    if not user:
        user = frappe.session.user

    # Allow Administrator full access
    if user == "Administrator":
        return True

    lab = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        "custom_lab_name"
    )

    if not lab:
        return False

    if doc.login_lab_name != lab:
        return False

    return True