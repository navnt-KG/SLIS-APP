# import frappe
# from frappe.model.document import Document
# from frappe.model.naming import make_autoname


# class SoilTestResult(Document):
#     def autoname(self):
#         # 1. Administrator Bypass
#         if frappe.session.user == "Administrator":
#             self.name = make_autoname("ADM-STR-.#####")
#             return

#         # 2. Fetch Lab Name from Employee record
#         user_full_lab_name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "custom_lab_name")
        
#         if not user_full_lab_name:
#             frappe.throw(f"User {frappe.session.user} is not linked to an Employee record with a Lab assigned.")
        
#         # 3. Lab Abbreviation Mapping
#         lab_abbreviation_map = {
#             "Hi-Tech Soil Analytical Lab WYD": "WYD",
#             "Regional Soil Analytical Laboratory Alappuzha": "ALP",
#             "Regional Soil Analytical Laboratory Kozhikode": "KZK",
#             "Regional Soil Analytical Laboratory Thrissur": "TSR",
#             "Soil and Plant Health Clinic, Kasaragod": "KSD",
#             "Soil and Plant Health Clinic, Pathanamthitta": "PTA",
#             "Central Soil Analytical Lab, Parottukonam": "TVM"
#         }

#         lab_code = lab_abbreviation_map.get(user_full_lab_name)
#         if not lab_code:
#             frappe.throw(f"Naming prefix not found for lab: {user_full_lab_name}")

#         # 4. Generate Final Name (STR for Soil Test Result)
#         # Format: STR-ALP-00001
#         self.name = make_autoname(f"STR-{lab_code}-.#####")

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SoilTestResult(Document):
    def autoname(self):
        # 1. Administrator Bypass
        if frappe.session.user == "Administrator":
            self.name = make_autoname("ADM-STR-.#####")
            return

        # 2. Define Mappings
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
            "Trivandrum": "TVC", 
            "Kollam": "QLN", 
            "Pathanamthitta": "PTA",
            "Alappuzha": "ALP", 
            "Kottayam": "KTM", 
            "Idukki": "IDU",
            "Ernakulam": "ERS", 
            "Thrissur": "TSR", 
            "Palakkad": "PGT", 
            "Malappuram": "MLP",
            "Kozhikode": "KZK",
            "Wayanad": "WAY",
            "Kannur": "CAN", 
            "Kasaragod": "KGQ"
        }

        # 3. Fetch Employee Data
        employee = frappe.db.get_value(
            "Employee", 
            {"user_id": frappe.session.user}, 
            ["custom_lab_name", "custom_district_office_name"], 
            as_dict=True
        )
        
        if not employee:
            frappe.throw(f"User {frappe.session.user} is not linked to an Employee record.")

        # 4. Determine Lab/District Code
        lab_code = None
        
        # Check Lab Name first
        if employee.custom_lab_name:
            lab_code = lab_map.get(employee.custom_lab_name)
        
        # Fallback to District Office
        if not lab_code and employee.custom_district_office_name:
            lab_code = district_map.get(employee.custom_district_office_name)

        # 5. Validation Check
        if not lab_code:
            frappe.throw("Neither a valid Lab nor a District Office was found for your Employee record to generate an ID.")

        # 6. Generate Final Name (STR for Soil Test Result)
        # Format: STR-TVC-00001
        self.name = make_autoname(f"STR-{lab_code}-.#####")




@frappe.whitelist()
def generate_recommendation(docname):

    doc = frappe.get_doc("Soil Test Result", docname)

    organic_carbon = None
    available_p = None
    available_k = None


    # -----------------------------------
    #  Extract Test Values
    # -----------------------------------

    for row in doc.results_table:
        if row.test_item and "Organic Carbon" in row.test_item:
            organic_carbon = float(row.final_result)
        elif row.test_item and "Available Phosphorous" in row.test_item:
            available_p = float(row.final_result)
        elif row.test_item and "Available Potassium" in row.test_item:
            available_k = float(row.final_result)


#     frappe.msgprint(f"""
# STEP 1 - TEST VALUES

# Organic Carbon: {organic_carbon}
# Available P: {available_p}
# Available K: {available_k}
# """)


    # -----------------------------------
    #  Find Fertility Adjustment
    # -----------------------------------

    adjustments = frappe.get_all("Fertility Adjustment Table", fields=["*"])

    n_adjust = 100
    pk_adjust = 100

    for adj in adjustments:

        oc_min = float(adj.oc_sandy_min or 0)
        oc_max = float(adj.oc_sandy_max or 0)

        p_min = float(adj.avail_p_min or 0)
        p_max = float(adj.avail_p_max or 0)

        k_min = float(adj.avail_k_min or 0)
        k_max = float(adj.avail_k_max or 0)

#         frappe.msgprint(f"""
# CHECKING FERTILITY ROW

# OC Range: {oc_min} - {oc_max}
# P Range: {p_min} - {p_max}
# K Range: {k_min} - {k_max}

# N Adj: {adj.n_adjustment}
# PK Adj: {adj.p_and_k_adjustment}
# """)


        if organic_carbon is not None:
            if oc_min <= organic_carbon <= oc_max:
                n_adjust = float(adj.n_adjustment)
                # frappe.msgprint(f"N MATCH FOUND → Adjustment = {n_adjust}")


        if available_p is not None:
            if p_min <= available_p <= p_max:
                pk_adjust = float(adj.p_and_k_adjustment)
                # frappe.msgprint(f"P MATCH FOUND → PK Adjustment = {pk_adjust}")


        if available_k is not None:
            if k_min <= available_k <= k_max:
                pk_adjust = float(adj.p_and_k_adjustment)
                # frappe.msgprint(f"K MATCH FOUND → PK Adjustment = {pk_adjust}")


#     frappe.msgprint(f"""
# STEP 2 RESULT

# N Adjustment = {n_adjust}
# PK Adjustment = {pk_adjust}
# """)


    # -----------------------------------
    #  Get Crop List
    # -----------------------------------

    register = frappe.get_doc("Register", doc.sample_id)

    # frappe.msgprint(f"Register Loaded → {register.name}")

    doc.recommendations_table = []


    # -----------------------------------
    #  Process Each Crop
    # -----------------------------------

    for crop_row in register.crops_list:

        crop = crop_row.crop_name

      # frappe.msgprint(f"PROCESSING CROP → {crop}")


        pop_name = frappe.db.get_value(
            "Package of Practice",
            {"crop": crop},
            "name"
        )

        if not pop_name:
            # frappe.msgprint(f"No Package of Practice found for {crop}")
            continue


        pop = frappe.get_doc("Package of Practice", pop_name)

        # frappe.msgprint(f"PoP Found → {pop_name}")


        n_required = 0
        p_required = 0
        k_required = 0
        n_unit = '' 
        p_unit = ''  
        k_unit = '' 


        # -----------------------------------
        #  Read PoP Nutrient Values
        # -----------------------------------

 
        for nutrient in pop.nutrient_data:
            if nutrient.nutrient and "Available Nitrogen" in nutrient.nutrient and organic_carbon is not None:
                n_required = float(nutrient.quantity) * n_adjust / 100
                n_unit = nutrient.unit or ''  # ADD THIS
            elif nutrient.nutrient and "Available Phosphorous" in nutrient.nutrient and available_p is not None:
                p_required = float(nutrient.quantity) * pk_adjust / 100
                p_unit = nutrient.unit or ''  # ADD THIS
            elif nutrient.nutrient and "Available Potassium" in nutrient.nutrient and available_k is not None:
                k_required = float(nutrient.quantity) * pk_adjust / 100
                k_unit = nutrient.unit or ''  # ADD THIS


#             frappe.msgprint(f"""
# PoP Nutrient Row

# Nutrient: {nutrient.nutrient}
# Quantity: {nutrient.quantity}
# """)


            # if nutrient.nutrient == "Available Nitrogen" and organic_carbon is not None:
            #     n_required = float(nutrient.quantity) * n_adjust / 100

            # elif nutrient.nutrient == "Available Phosphorous" and available_p is not None:
            #     p_required = float(nutrient.quantity) * pk_adjust / 100

            # elif nutrient.nutrient == "Available Potassium" and available_k is not None:
            #     k_required = float(nutrient.quantity) * pk_adjust / 100


#         frappe.msgprint(f"""
# STEP 3 - NUTRIENT REQUIREMENT

# N Required: {n_required}
# P Required: {p_required}
# K Required: {k_required}
# """)


        # -----------------------------------
        #  Get Fertilizers
        # -----------------------------------

        fert_n = None
        fert_p = None
        fert_k = None


        fert_n_name = frappe.db.get_value(
        "Fertilizer",
        {"primary_nutrient": ["like", "%Available Nitrogen%"]},
        "name"
        )

        fert_p_name = frappe.db.get_value(
            "Fertilizer",
            {"primary_nutrient": ["like", "%Available Phosphorous%"]},
            "name"
        )

        fert_k_name = frappe.db.get_value(
            "Fertilizer",
            {"primary_nutrient": ["like", "%Available Potassium%"]},
            "name"
        )


#         frappe.msgprint(f"""
# FERTILIZER LOOKUP

# N Fertilizer: {fert_n_name}
# P Fertilizer: {fert_p_name}
# K Fertilizer: {fert_k_name}
# """)


        if fert_n_name:
            fert_n = frappe.get_doc("Fertilizer", fert_n_name)

        if fert_p_name:
            fert_p = frappe.get_doc("Fertilizer", fert_p_name)

        if fert_k_name:
            fert_k = frappe.get_doc("Fertilizer", fert_k_name)


        # -----------------------------------
        #  Convert Nutrient → Fertilizer
        # -----------------------------------

        urea = 0
        rajphos = 0
        potash = 0


        if fert_n and n_required > 0:
            urea = (n_required / float(fert_n.nutrient_percentage)) * 100

        if fert_p and p_required > 0:
            rajphos = (p_required / float(fert_p.nutrient_percentage)) * 100

        if fert_k and k_required > 0:
            potash = (k_required / float(fert_k.nutrient_percentage)) * 100


#         frappe.msgprint(f"""
# FINAL FERTILIZER CALCULATION

# Urea: {urea}
# Rajphos: {rajphos}
# Potash: {potash}
# """)


        # -----------------------------------
        #  Add Recommendation Row
        # -----------------------------------

        row = doc.append("recommendations_table", {})

        row.crop = crop
        row.urea = round(urea, 2)
        row.rajphos = round(rajphos, 2)
        row.potash = round(potash, 2)
        row.unit = n_unit



    # -----------------------------------
    #  Save Document
    # -----------------------------------

    doc.save(ignore_permissions=True)

    frappe.msgprint("Recommendation Generated Successfully")

    return "Recommendation Generated"




