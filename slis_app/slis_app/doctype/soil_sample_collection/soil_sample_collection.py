# import frappe
# from frappe.model.document import Document
# from frappe.model.naming import make_autoname
# from frappe.utils import nowdate


# class SoilSampleCollection(Document):

#     def autoname(self):

#         if not self.client_type:
#             frappe.throw("Client Type is required")

#         if not self.reference_name:
#             frappe.throw("Reference Name is required")

#         prefix_map = {
#             "Farmer": "FS",
#             "Department": "DS",
#             "Consultancy": "CS"
#         }

#         prefix = prefix_map.get(self.client_type)
#         if not prefix:
#             frappe.throw("Invalid Client Type")

#         ref = self.reference_name.strip().upper().replace(" ", "-")

#         self.name = make_autoname(f"{prefix}-{ref}-.#####")









#for the naming series

# import frappe
# from frappe.model.document import Document
# from frappe.model.naming import make_autoname

# class SoilSampleCollection(Document):
#     def autoname(self):
#         # --- Administrator Bypass ---
#         if frappe.session.user == "Administrator":
#             # For Administrator, use a simple generic series or skip lab-based logic
#             self.name = make_autoname("ADM-SSC-.#####")
#             return

#         # 1. Basic Validations
#         if not self.client_type:
#             frappe.throw("Client Type is required")
#         if not self.reference_name:
#             frappe.throw("Reference Name is required")

#         # 2. Map Client Type to Prefix
#         prefix_map = {
#             "Farmer": "FS",
#             "Department": "DS",
#             "Consultancy": "CS"
#         }
#         prefix = prefix_map.get(self.client_type)
#         if not prefix:
#             frappe.throw("Invalid Client Type")

#         # 3. Lab Abbreviation Mapping
#         # Keys must match the exact "Full Name" stored in the 'custom_lab_name' field
#         lab_abbreviation_map = {
#             "Hi-Tech Soil Analytical Lab WYD": "WYD",
#             "Regional Soil Analytical Laboratory Alappuzha": "ALP",
#             "Regional Soil Analytical Laboratory Kozhikode": "KZK",
#             "Regional Soil Analytical Laboratory Thrissur": "TSR",
#             "Soil and Plant Health Clinic, Kasaragod": "KSD",
#             "Soil and Plant Health Clinic, Pathanamthitta": "PTA",
#             "Central Soil Analytical Lab, Parottukonam": "TVM"
#         }

#         # 4. Fetch Lab Name from the logged-in User's Employee Record
#         user_full_lab_name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "custom_lab_name")
        
#         if not user_full_lab_name:
#             frappe.throw(f"User {frappe.session.user} is not linked to an Employee record or a Lab.")

#         # Get the abbreviation from our map
#         lab_code = lab_abbreviation_map.get(user_full_lab_name)

#         if not lab_code:
#             # Fallback or error if the lab name doesn't match the map exactly
#             frappe.throw(f"Lab '{user_full_lab_name}' does not have a defined naming abbreviation.")

#         # 5. Process Reference Name
#         ref = self.reference_name.strip().upper().replace(" ", "-")

#         # 6. Generate Final Name: Prefix-LABCODE-REF-.#####
#         # Example Output: FS-RSAL_ALP-REFNAME-00001
#         self.name = make_autoname(f"{prefix}-{lab_code}-{ref}-.#####")


#     def validate(self):

#         user = frappe.session.user
#         roles = frappe.get_roles()

#         # Skip validation for Administrator
#         if user != "Administrator":

#             if "PSC Officer" in roles:

#                 if self.employee_type == "Lab":
#                     frappe.throw("PSC Officer cannot edit Lab records")

#                 if self.status not in ["With PSC Officer", "Returned to PSC Officer (Overload)"]:
#                     frappe.throw(
#                         "Edit allowed only when status is 'With PSC Officer' or 'Returned to PSC Officer (Overload)'"
#                     )

#new code 


import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SoilSampleCollection(Document):
    def autoname(self):
        # --- Administrator Bypass ---
        if frappe.session.user == "Administrator":
            self.name = make_autoname("ADM-SSC-.#####")
            return

        # 1. Basic Validations
        if not self.client_type:
            frappe.throw("Client Type is required for naming.")

        # Reference name required only for specific types
        if self.client_type in ["Farmer", "Consultancy"] and not self.reference_name:
            frappe.throw("Reference Name is required for this Client Type.")

        # 2. Map Client Type to Prefix
        prefix_map = {"Farmer": "FS", "Department": "DS", "Consultancy": "CS"}
        prefix = prefix_map.get(self.client_type, "SS")

        # 3. Define Combined Mappings

        # Lab Mappings
        lab_map = {
            "Hi-Tech Soil Analytical Lab WYD": "WYD",
            "Regional Soil Analytical Laboratory Alappuzha": "ALP",
            "Regional Soil Analytical Laboratory Kozhikode": "KZK",
            "Regional Soil Analytical Laboratory Thrissur": "TSR",
            "Soil and Plant Health Clinic, Kasaragod": "KSD",
            "Soil and Plant Health Clinic, Pathanamthitta": "PTA",
            "Central Soil Analytical Lab, Parottukonam": "TVM"
        }
        
        # District Office Mappings
        district_map = {
            "Trivandrum": "TVC", 
            "Kollam": "QLN", 
            "Pathanamthitta": "PTA",
            "Alappuzha": "ALP", 
            "Kottayam": "KTM", 
            "Idukki": "IDU",
            "Ernakulam": "ERS", 
            "Thrissur": "TSR", 
            "Palakad": "PGT",
            "Malappuram": "MLP", 
            "Kozhikode": "KZK", 
            "Wayanad": "WAY",
            "Kannur": "CAN", 
            "Kasaragod": "KGQ"
        }

        # 4. Fetch Employee Data
        employee_data = frappe.db.get_value(
            "Employee", 
            {"user_id": frappe.session.user}, 
            ["custom_lab_name", "custom_district_office_name"], 
            as_dict=True
        )
        
        if not employee_data:
            frappe.throw(f"User {frappe.session.user} is not linked to an Employee record.")

        # 5. Determine Lab/District Code
        lab_code = None
        
        # Check Lab Name first
        if employee_data.custom_lab_name:
            lab_code = lab_map.get(employee_data.custom_lab_name)
        
        # If no Lab Code found, fallback to District Office Name
        if not lab_code and employee_data.custom_district_office_name:
            lab_code = district_map.get(employee_data.custom_district_office_name)

        if not lab_code:
            frappe.throw("Neither a valid Lab nor a District Office was found for your Employee record.")

        # 6. Process Reference Name and Generate Final Name
        if self.reference_name:
            ref = self.reference_name.strip().upper().replace(" ", "-")
        else:
            ref = "GEN"   # fallback for Department or empty cases

        self.name = make_autoname(f"{prefix}-{lab_code}-{ref}-.#####")

    def validate(self):

        user = frappe.session.user
        roles = frappe.get_roles()

        # Skip validation for Administrator
        if user != "Administrator":

            if "PSC Officer" in roles:

                if self.employee_type == "Lab":
                    frappe.throw("PSC Officer cannot edit Lab records")

                if self.status not in ["With PSC Officer", "Returned to PSC Officer (Overload)"]:
                    frappe.throw(
                        "Edit allowed only when status is 'With PSC Officer' or 'Returned to PSC Officer (Overload)'"
                    )