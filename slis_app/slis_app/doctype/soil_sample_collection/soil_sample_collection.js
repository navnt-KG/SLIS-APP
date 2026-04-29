// frappe.ui.form.on("Soil Sample Collection", {
//     refresh(frm) {

//         console.log("App JS loaded");

//         if (!frm.is_new() && frm.doc.docstatus === 0) {

//             frm.add_custom_button(__('Add Sample'), function () {
//                 frappe.new_doc('Soil Sample Collection', {
//                     client: frm.doc.client,
//                     reference_name: frm.doc.reference_name
//                 });
//             });

//         }
//     }
// });



// frappe.ui.form.on('Soil Sample Collection', {
//     refresh: function(frm) {

//         if (frappe.user.has_role("Senior Chemist")) {

//             // When user clicks Assign To in sidebar
//             $(document).on("click", ".add-assignment", function () {

//                 // Wait for dialog to render
//                 setTimeout(function () {

//                     let dialog = $(".frappe-dialog:visible");

//                     if (dialog.length) {

//                         // Hide "Assign to me" checkbox
//                         dialog.find("label:contains('Assign to me')")
//                               .closest(".form-group")
//                               .hide();

//                     }

//                 }, 200);

//             });

//         }
//     }
// });




// frappe.ui.form.on('Soil Sample Collection', {
//     refresh: function(frm) {
//         // Hide default primary action (like 'Save')
//         frm.page.clear_primary_action();

//         if (!frm.is_new()) {
//             // Add custom primary button
//             frm.add_custom_button(__('Add to Register'), () => {
                
//                 // 1. Validate status
//                 let current_status = frm.doc.status;
//                 if (current_status !== "With Research Assistant") {
//                     frappe.msgprint({
//                         title: __('Status Error'),
//                         indicator: 'red',
//                         message: __('Either not assigned/ Completed!')
//                     });
//                     return;
//                 }

//                 // 2. Map data and redirect
//                 create_register_from_form(frm);

//             }).addClass('btn-primary'); // Makes the button blue/primary
//         }
//     }
// });

// /**
//  * Handles the data transfer from Soil Sample Collection to a new Register document
//  */
// function create_register_from_form(frm) {
//     frappe.model.with_doctype('Register', () => {
//         // Create a local unsaved document in the 'Register' Doctype
//         let new_doc = frappe.model.get_new_doc('Register');

//         // Map Parent Fields
//         new_doc.source_sample_id = frm.doc.name;
//         new_doc.latitude = frm.doc.latitude;
//         new_doc.longitude = frm.doc.longitude;
//         new_doc.client_type = frm.doc.client_type;
//         new_doc.plot_size = frm.doc.plot_size;
//         // Adding client field as per your previous snippet
//         new_doc.client = frm.doc.client; 

//         // Map Child Table: tests
//         if (frm.doc.tests && frm.doc.tests.length > 0) {
//             frm.doc.tests.forEach(row => {
//                 let child = frappe.model.add_child(new_doc, 'tests');
//                 child.test_name = row.test_name;
//             });
//         }

//         // Map Child Table: crops_list
//         if (frm.doc.crops_list && frm.doc.crops_list.length > 0) {
//             frm.doc.crops_list.forEach(row => {
//                 let child = frappe.model.add_child(new_doc, 'crops_list');
//                 child.crop_name = row.crop_name;
//             });
//         }

//         // Refresh the local doc reference and route to the Form
//         frappe.set_route('Form', 'Register', new_doc.name);
//     });
// }

frappe.ui.form.on("Soil Sample Collection", {
    refresh(frm) {

        console.log("Backend JS loaded");

        // Add Sample Button
        if (!frm.is_new() && frm.doc.docstatus === 0) {

            frm.add_custom_button(__('Add Sample'), function () {
                frappe.new_doc('Soil Sample Collection', {
                    client: frm.doc.client,
                    reference_name: frm.doc.reference_name
                });
            });
        }

        // Remove default Save
        frm.page.clear_primary_action();

        // Add to Register Button
        if (!frm.is_new()) {

            frm.add_custom_button(__('Add to Register'), () => {

                let current_status = frm.doc.status;

                if (current_status !== "With Research Assistant") {
                    frappe.msgprint({
                        title: __('Status Error'),
                        indicator: 'red',
                        message: __('Either not assigned/ Completed!')
                    });
                    return;
                }

                create_register_from_form(frm);

            }).addClass('btn-primary');
        }
    }
});


// =========================
// CREATE REGISTER
// =========================
function create_register_from_form(frm) {

    frappe.model.with_doctype('Register', () => {

        let new_doc = frappe.model.get_new_doc('Register');

        // ✅ BASIC
        new_doc.source_sample_id = frm.doc.name;
        new_doc.latitude = frm.doc.latitude;
        new_doc.longitude = frm.doc.longitude;
        new_doc.client_type = frm.doc.client_type;
        new_doc.plot_size = frm.doc.plot_size;
        new_doc.client = frm.doc.client;

        // 🔥 IMPORTANT FIX (YOU MISSED BEFORE)
        new_doc.name_of_type = frm.doc.name_of_type;
        new_doc.type_of_collection = frm.doc.type_of_collection;
        new_doc.number_of_samples = frm.doc.number_of_samples;
        new_doc.lab_code_prefix = frm.doc.lab_code_prefix;
        new_doc.lab_code_start = frm.doc.lab_code_start;
        // 🔥 TABLE COPY
        new_doc.register_sample_data = [];

        if (frm.doc.sample_data && frm.doc.sample_data.length > 0) {

            frm.doc.sample_data.forEach(row => {

                new_doc.register_sample_data.push({
                    sample_id: row.sample_id,
                    values_json: row.values_json,
                    lab_code: row.lab_code
                });

            });
        }

        // ✅ TESTS
        if (frm.doc.tests && frm.doc.tests.length > 0) {

            frm.doc.tests.forEach(row => {

                let child = frappe.model.add_child(new_doc, 'tests');
                child.test_name = row.test_name;

            });
        }

        // ✅ CROPS
        if (frm.doc.crops_list && frm.doc.crops_list.length > 0) {

            frm.doc.crops_list.forEach(row => {

                let child = frappe.model.add_child(new_doc, 'crops_list');
                child.crop_name = row.crop_name;

            });
        }

        // 🚀 OPEN REGISTER
        frappe.set_route('Form', 'Register', new_doc.name);
    });
}