// frappe.listview_settings['Soil Sample Collection'] = {
//     refresh(listview) {
//         listview.page.clear_inner_buttons();

//         listview.page.add_inner_button(__('Add to Register'), () => {
//             const selected_items = listview.get_checked_items();

//             if (!selected_items.length) {
//                 frappe.msgprint(__('Please select at least one sample to register.'));
//                 return;
//             }

//             selected_items.forEach(doc => {
//                 create_register_from_list(doc);
//             });
//         });
//     }
// };

// //  FUNCTION GOES IN THE SAME FILE
// function create_register_from_list(source_doc) {
//     frappe.model.with_doctype('Register', function () {

//         let new_doc = frappe.model.get_new_doc('Register');

//         new_doc.latitude = source_doc.latitude;
//         new_doc.longitude = source_doc.longitude;
//         new_doc.client_type = source_doc.client_type;
//         new_doc.source_sample_id = source_doc.name;

//         frappe.db.get_doc('Soil Sample Collection', source_doc.name).then(full_doc => {

//             if (full_doc.tests && full_doc.tests.length > 0) {

//                 full_doc.tests.forEach(test_row => {
//                     let child = frappe.model.add_child(new_doc, 'tests');
//                     child.test_name = test_row.test_name;
//                 });

//                 frappe.db.insert(new_doc).then(() => {
//                     frappe.show_alert({
//                         message: __('{0} added to Register', [source_doc.name]),
//                         indicator: 'green'
//                     });
//                 });

//             } else {
//                 frappe.msgprint(__('Sample {0} has no tests selected.', [source_doc.name]));
//             }
//         });
//     });
// }







// frappe.listview_settings['Soil Sample Collection'] = {
//     refresh(listview) {
//         // 1. Hide the default "Add Soil Sample Collection" button
//         // Using a more robust selector that finds the button by text/attribute
//         $(".primary-action:contains('Add Soil Sample Collection')").hide();

//         // 2. Set your custom primary action
//         listview.page.set_primary_action(__('Add Soil Sample'), () => {
//              frappe.new_doc('Clients');
//         });

//         // 3. Add "Add to Register" to the inner toolbar
//         // Remove it first to ensure we don't have duplicates or stale references
//         listview.page.remove_inner_button(__('Add to Register'));

//         listview.page.add_inner_button(__('Add to Register'), () => {
//             const selected_items = listview.get_checked_items();
            
//             if (selected_items.length === 0) {
//                 frappe.msgprint(__('Please select at least one sample to register.'));
//                 return;
//             }

//             // Logic for processing selected items
//             selected_items.forEach(doc => {
//                 // Ensure create_register_from_list is defined in this scope or globally
//                 if (typeof create_register_from_list === "function") {
//                     create_register_from_list(doc);
//                 } else {
//                     console.error("Function create_register_from_list is not defined.");
//                 }
//             });
//         });
//     }
// };








// frappe.listview_settings['Soil Sample Collection'] = {
//     refresh(listview) {

//         listview.page.clear_primary_action();

//         listview.page.set_primary_action(__('Add Soil Sample'), () => {
//             frappe.new_doc('Clients');
//         });

//         // ✅ Always add button (Frappe handles duplicates internally)
//         listview.page.add_inner_button(__('Add to Register'), () => {

//             const selected_items = listview.get_checked_items();

//             if (!selected_items.length) {
//                 frappe.msgprint(__('Please select at least one sample to register.'));
//                 return;
//             }

//             selected_items.forEach(doc => {
//                 create_register_from_list(doc);
//             });

//         }, __('Actions'));  // 👈 VERY IMPORTANT (puts inside Actions dropdown)
//     }
// };