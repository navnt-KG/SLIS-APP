import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SoilSampleCollection(Document):

    # =====================================================
    # AUTONAME
    # =====================================================

    def autoname(self):

        # =========================================
        # GENERATED SAMPLE VARIANT
        # =========================================

        if self.is_generated_sample:

            self.name = (
                f"{self.parent_sample}-"
                f"{self.variant_number}"
            )

            return

        # =========================================
        # ADMINISTRATOR
        # =========================================

        if frappe.session.user == "Administrator":

            self.name = make_autoname(
                "ADM-SSC-.#####"
            )

            return

        # =========================================
        # BASIC VALIDATION
        # =========================================

        if not self.client_type:

            frappe.throw(
                "Client Type is required for naming."
            )

        # =========================================
        # REFERENCE NAME CHECK
        # =========================================

        if (
            self.client_type in [
                "Farmer",
                "Consultancy"
            ]
            and
            not self.reference_name
        ):

            frappe.throw(
                "Reference Name is required "
                "for this Client Type."
            )

        # =========================================
        # PREFIX MAP
        # =========================================

        prefix_map = {
            "Farmer": "FS",
            "Department": "DS",
            "Consultancy": "CS"
        }

        prefix = prefix_map.get(
            self.client_type,
            "SS"
        )

        # ===========================frappe-bench==============
        # LAB MAP
        # =========================================

        lab_map = {

            "Hi-Tech Soil Analytical Lab WYD": "WYD",

            "Regional Soil Analytical Laboratory Alappuzha": "ALP",

            "Regional Soil Analytical Laboratory Kozhikode": "KZK",

            "Regional Soil Analytical Laboratory Thrissur": "TSR",

            "Soil and Plant Health Clinic, Kasaragod": "KSD",

            "Soil and Plant Health Clinic, Pathanamthitta": "PTA",

            "Central Soil Analytical Lab, Parottukonam": "TVM"
        }

        # =========================================
        # DISTRICT MAP
        # =========================================

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

        # =========================================
        # EMPLOYEE DATA
        # =========================================

        employee_data = frappe.db.get_value(

            "Employee",

            {"user_id": frappe.session.user},

            [
                "custom_lab_name",
                "custom_district_office_name"
            ],

            as_dict=True
        )

        if not employee_data:

            frappe.throw(
                f"User {frappe.session.user} "
                f"is not linked to an Employee record."
            )

        # =========================================
        # LAB CODE
        # =========================================

        lab_code = None

        # LAB NAME

        if employee_data.custom_lab_name:

            lab_code = lab_map.get(
                employee_data.custom_lab_name
            )

        # DISTRICT OFFICE

        if (
            not lab_code
            and
            employee_data.custom_district_office_name
        ):

            lab_code = district_map.get(
                employee_data.custom_district_office_name
            )

        if not lab_code:

            frappe.throw(
                "Neither a valid Lab nor a "
                "District Office was found "
                "for your Employee record."
            )

        # =========================================
        # FINAL NAME
        # =========================================

        if self.reference_name:

            ref = (
                self.reference_name
                .strip()
                .upper()
                .replace(" ", "-")
            )

            self.name = make_autoname(
                f"{prefix}-{lab_code}-{ref}-.#####"
            )

        else:

            self.name = make_autoname(
                f"{prefix}-{lab_code}-.#####"
            )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(self):

        user = frappe.session.user

        roles = frappe.get_roles()

        # =========================================
        # SKIP ADMIN
        # =========================================

        if user != "Administrator":

            if "PSC Officer" in roles:

                if self.employee_type == "Lab":

                    frappe.throw(
                        "PSC Officer cannot edit Lab records"
                    )

                old_doc = self.get_doc_before_save()

                previous_status = ""

                if old_doc:

                    previous_status = old_doc.status

                if (
                    (previous_status or "").strip()
                    not in [
                        "With PSC Officer",
                        "Returned to PSC Officer (Overload)"
                    ]
                ):

                    frappe.throw(
                        "Edit allowed only when "
                        "status is "
                        "'With PSC Officer' "
                        "or "
                        "'Returned to PSC Officer (Overload)'"
                    )

    # =====================================================
    # ON UPDATE
    # =====================================================

    def on_update(self):

        # =========================================
        # ONLY MASTER SAMPLE
        # =========================================

        if (
            self.is_master_sample
            and
            not self.is_generated_sample
            and
            self.client_type in ["Department", "Consultancy"]
        ):

            # =====================================
            # CREATE VARIANTS
            # =====================================

            self.create_sample_variants()

            # =====================================
            # SYNC STATUS TO VARIANTS
            # =====================================

            self.sync_variant_status()

    # =====================================================
    # SYNC VARIANT STATUS
    # =====================================================

    def sync_variant_status(self):

        # =========================================
        # GET VARIANTS
        # =========================================

        variants = frappe.get_all(

            self.doctype,

            filters={
                "parent_sample": self.name
            },

            pluck="name"
        )

        if not variants:
            return

        # =========================================
        # UPDATE VARIANTS
        # =========================================

        for variant_name in variants:

            variant_doc = frappe.get_doc(
                self.doctype,
                variant_name
            )

            # =====================================
            # COPY STATUS
            # =====================================

            variant_doc.status = self.status

            # =====================================
            # OPTIONAL FIELD COPY
            # =====================================

            # variant_doc.target_lab = self.target_lab

            # variant_doc.assigned_to = self.assigned_to

            # =====================================
            # SAVE
            # =====================================

            variant_doc.flags.ignore_validate = True

            variant_doc.save(
                ignore_permissions=True
            )

        frappe.db.commit()

    # =====================================================
    # CREATE SAMPLE VARIANTS
    # =====================================================

    def create_sample_variants(self):

        # =========================================
        # PREVENT DUPLICATES
        # =========================================

        existing = frappe.get_all(

            self.doctype,

            filters={
                "parent_sample": self.name
            }
        )

        if existing:

            return

        # =========================================
        # NO SAMPLE DATA
        # =========================================

        if not self.sample_data:

            return

        # =========================================
        # LOOP CHILD ROWS
        # =========================================

        for idx, row in enumerate(
            self.sample_data,
            start=1
        ):

            # =====================================
            # CREATE NEW DOC
            # =====================================

            new_doc = frappe.new_doc(
                self.doctype
            )

            # =====================================
            # COPY MAIN FIELDS
            # =====================================

            for field in self.meta.fields:

                fieldname = field.fieldname

                # SKIP TABLES

                if field.fieldtype in [
                    "Table",
                    "Section Break",
                    "Column Break",
                    "HTML"
                ]:

                    continue

                # SKIP SYSTEM FIELDS

                if fieldname in [

                    "name",
                    "owner",
                    "creation",
                    "modified",
                    "modified_by",
                    "docstatus"
                ]:

                    continue

                # SKIP VARIANT FIELDS

                if fieldname in [

                    "is_master_sample",
                    "is_generated_sample",
                    "parent_sample",
                    "variant_number"
                ]:

                    continue

                new_doc.set(
                    fieldname,
                    self.get(fieldname)
                )

            # =====================================
            # VARIANT SETTINGS
            # =====================================

            new_doc.is_master_sample = 0

            new_doc.is_generated_sample = 1

            new_doc.parent_sample = self.name

            new_doc.variant_number = idx

            # =====================================
            # VARIANT DOCUMENT NAME
            # =====================================

            new_doc.name = (
                f"{self.name}-{idx}"
            )

            # =====================================
            # CLEAR CHILD TABLE
            # =====================================

            new_doc.sample_data = []

            # =====================================
            # ADD SINGLE CHILD ROW
            # =====================================

            child = new_doc.append(
                "sample_data",
                {}
            )

            # =====================================
            # COPY CHILD ROW VALUES
            # =====================================

            for child_field in row.meta.fields:

                child_fieldname = (
                    child_field.fieldname
                )

                # SKIP SYSTEM CHILD FIELDS

                if child_fieldname in [

                    "name",
                    "parent",
                    "parentfield",
                    "parenttype",
                    "idx"
                ]:

                    continue

                child.set(
                    child_fieldname,
                    row.get(child_fieldname)
                )

            # =====================================
            # KEEP ORIGINAL SAMPLE ID
            # =====================================

            original_sample_id = row.sample_id

            child.sample_id = original_sample_id

            new_doc.reference_sample_id = (
                original_sample_id
            )

            # =====================================
            # VARIANT REFERENCE
            # =====================================

            child.variant_reference = (
                f"{self.name}-{idx}"
            )

            # =====================================
            # SINGLE SAMPLE
            # =====================================

            new_doc.number_of_samples = 1

            # =====================================
            # SAVE
            # =====================================

            new_doc.flags.ignore_mandatory = True

            new_doc.insert(
                ignore_permissions=True
            )

        # =========================================
        # COMMIT
        # =========================================

        frappe.db.commit()








