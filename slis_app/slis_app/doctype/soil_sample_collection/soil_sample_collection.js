// Copyright (c) 2026, navaneeth and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Soil Sample Collection", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Soil Sample Collection", {
    refresh(frm) {

        console.log("App JS loaded");

        if (!frm.is_new() && frm.doc.docstatus === 0) {

            frm.add_custom_button(__('Add Sample'), function () {
                frappe.new_doc('Soil Sample Collection', {
                    client: frm.doc.client,
                    reference_name: frm.doc.reference_name
                });
            });

        }
    }
});



frappe.ui.form.on('Soil Sample Collection', {
    refresh: function(frm) {

        if (frappe.user.has_role("Senior Chemist")) {

            // When user clicks Assign To in sidebar
            $(document).on("click", ".add-assignment", function () {

                // Wait for dialog to render
                setTimeout(function () {

                    let dialog = $(".frappe-dialog:visible");

                    if (dialog.length) {

                        // Hide "Assign to me" checkbox
                        dialog.find("label:contains('Assign to me')")
                              .closest(".form-group")
                              .hide();

                    }

                }, 200);

            });

        }
    }
});



//code for the add to register in the form view


frappe.ui.form.on('Soil Sample Collection', {
    refresh: function(frm) {

        frm.page.clear_primary_action();

        if (!frm.is_new()) {
            frm.add_custom_button(__('Add to Register'), () => {

                //  Validate status before proceeding
                //  Change this to 'status' if you're NOT using workflow
                let current_status = frm.doc.status;

                if (current_status !== "With Research Assistant") {
                    frappe.msgprint(__('Only the samples that are with RA are allowed to move to register.'));
                    return; //  Stop here
                }

                // If valid, proceed
                create_register_from_list(frm.doc);
            });
        }
    }
});

function create_register_from_list(doc) {
    frappe.model.with_doctype('Register', () => {
        let new_reg = frappe.model.get_new_doc('Register');

        new_reg.source_sample_id = doc.name; 
        new_reg.client = doc.client; 

        frappe.set_route('Form', 'Register', new_reg.name);
    });
}