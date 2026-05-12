// frappe.ui.form.on("Soil Sample Collection", {
//     refresh(frm) {

//         console.log("Backend JS loaded");

//         // Add Sample Button
//         if (!frm.is_new() && frm.doc.docstatus === 0) {

//             frm.add_custom_button(__('Add Sample'), function () {
//                 frappe.new_doc('Soil Sample Collection', {
//                     client: frm.doc.client,
//                     reference_name: frm.doc.reference_name
//                 });
//             });
//         }

//         // Remove default Save
//         frm.page.clear_primary_action();

//         // ✅ MOVE TO TEST BUTTON
//         if (!frm.is_new()) {

//             frm.add_custom_button(__('Move to Test'), () => {

//                 console.log("Move to Test clicked");

//                 let current_status = frm.doc.status;

//                 if (current_status !== "With Research Assistant") {
//                     frappe.msgprint({
//                         title: __('Status Error'),
//                         indicator: 'red',
//                         message: __('Either not assigned/ Completed!')
//                     });
//                     return;
//                 }

//                 // 🔍 DUPLICATE CHECK
//                 frappe.call({
//                     method: "frappe.client.get_list",
//                     args: {
//                         doctype: "Soil Test Result",
//                         filters: {
//                             main_sample_id: frm.doc.name
//                         },
//                         fields: ["name"],
//                         limit_page_length: 1
//                     },
//                     callback: function (r) {

//                         console.log("API Response:", r);

//                         if (r && r.message && r.message.length > 0) {

//                             let existing_name = r.message[0].name;

//                             frappe.confirm(
//                                 `Soil Test Result already exists (${existing_name})<br><br>Open existing record?`,
//                                 function () {
//                                     frappe.set_route('Form', 'Soil Test Result', existing_name);
//                                 },
//                                 function () {}
//                             );

//                         } else {
//                             create_test_result(frm);
//                         }
//                     },

//                     error: function () {
//                         create_test_result(frm);
//                     }
//                 });

//             }).addClass('btn-primary');
//         }
//     }
// });


// // =========================
// // CREATE SOIL TEST RESULT
// // =========================
// function create_test_result(frm) {

//     frappe.model.with_doctype('Soil Test Result', () => {

//         let new_doc = frappe.model.get_new_doc('Soil Test Result');

//         // ✅ BASIC
//         new_doc.main_sample_id = frm.doc.name;
//         new_doc.client = frm.doc.client;
//         new_doc.client_type = frm.doc.client_type;

//         new_doc.latitude = frm.doc.latitude;
//         new_doc.longitude = frm.doc.longitude;
//         new_doc.plot_size = frm.doc.plot_size;

//         new_doc.name_of_type = frm.doc.name_of_type;
//         new_doc.type_of_collection = frm.doc.type_of_collection;
//         new_doc.number_of_sample = frm.doc.number_of_samples;

//         new_doc.lab_code_prefix = frm.doc.lab_code_prefix;
//         new_doc.lab_code_start = frm.doc.lab_code_start;

//         // 🔥 DATA MOVE
//         new_doc.test_sample_data = [];

//         // ✅ ONLY CHANGE (Farmer should skip sample_data)
//         if (frm.doc.client_type !== "Farmer" && frm.doc.sample_data && frm.doc.sample_data.length > 0) {

//             frm.doc.sample_data.forEach(row => {

//                 let is_consultancy = frm.doc.client_type === "Consultancy";

//                 new_doc.test_sample_data.push({
//                     sample_id: is_consultancy ? row.lab_code : row.sample_id,
//                     lab_code: row.lab_code,
//                     values_json: row.values_json || "{}"
//                 });

//             });
//         }

//         // // ✅ TESTS (ALL TYPES)
//         if (frm.doc.tests && frm.doc.tests.length > 0) {

//             frm.doc.tests.forEach(row => {

//                 let child = frappe.model.add_child(new_doc, 'results_table');
//                 child.test_item = row.test_name;

//             });
//         }


//         // ✅ CROPS (ALL TYPES)
//         if (frm.doc.crops_list && frm.doc.crops_list.length > 0) {

//             frm.doc.crops_list.forEach(row => {

//                 let child = frappe.model.add_child(new_doc, 'recommendations_table');
//                 child.crop = row.crop_name;

//             });
//         }

//         // 🚀 OPEN FORM
//         frappe.set_route('Form', 'Soil Test Result', new_doc.name);
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



 // ✅ MOVE TO TEST BUTTON

 if (!frm.is_new()&&frm.doc.status === "With Research Assistant") {



 frm.add_custom_button(__('Move to Test'), () => {



 console.log("Move to Test clicked");



 let current_status = frm.doc.status;



 if (current_status !== "With Research Assistant") {



 frappe.msgprint({

 title: __('Status Error'),

 indicator: 'red',

 message: __('Either not assigned/ Completed!')

 });



 return;

 }



 // 🔍 DUPLICATE CHECK

 frappe.call({

 method: "frappe.client.get_list",

 args: {

 doctype: "Soil Test Result",

 filters: {

 main_sample_id: frm.doc.name

 },

 fields: ["name"],

 limit_page_length: 1

 },



 callback: function (r) {



 console.log("API Response:", r);



 if (r && r.message && r.message.length > 0) {



 let existing_name = r.message[0].name;



 frappe.confirm(

 `Soil Test Result already exists (${existing_name})<br><br>Open existing record?`,



 function () {



 frappe.set_route(

 'Form',

 'Soil Test Result',

 existing_name

 );



 },



 function () {}



 );



 } else {



 create_test_result(frm);



 }

 },



 error: function () {



 create_test_result(frm);



 }

 });



 }).addClass('btn-primary');

 }

 }

});




// =========================

// CREATE SOIL TEST RESULT

// =========================

async function create_test_result(frm) {



 await frappe.model.with_doctype('Soil Test Result');



 let new_doc = frappe.model.get_new_doc('Soil Test Result');



 // ✅ BASIC

 new_doc.main_sample_id = frm.doc.name;



 new_doc.client = frm.doc.client;

 new_doc.client_type = frm.doc.client_type;



 new_doc.latitude = frm.doc.latitude;

 new_doc.longitude = frm.doc.longitude;



 new_doc.plot_size = frm.doc.plot_size;



 new_doc.name_of_type = frm.doc.name_of_type;



 new_doc.type_of_collection = frm.doc.type_of_collection;



 new_doc.number_of_sample = frm.doc.number_of_samples;



 new_doc.lab_code_prefix = frm.doc.lab_code_prefix;



 new_doc.lab_code_start = frm.doc.lab_code_start;



 // =========================

 // DATA MOVE

 // =========================

 new_doc.test_sample_data = [];



 // ✅ Farmer skip sample_data

 if (

 frm.doc.client_type !== "Farmer" &&

 frm.doc.sample_data &&

 frm.doc.sample_data.length > 0

 ) {



 frm.doc.sample_data.forEach(row => {



 let is_consultancy =

 frm.doc.client_type === "Consultancy";



 new_doc.test_sample_data.push({



 sample_id:

 is_consultancy

 ? row.lab_code

 : row.sample_id,



 lab_code: row.lab_code,



 values_json:

 row.values_json || "{}"



 });



 });

 }



 // =========================

 // TESTS

 // =========================

 for (let row of (frm.doc.tests || [])) {



 if (!row.test_name)

 continue;



 try {



 let pkg =

 await frappe.db.get_doc(

 'Soil Test Package',

 row.test_name

 );



 // ✅ INCLUDED TESTS EXISTS

 if (

 pkg.included_tests &&

 pkg.included_tests.length > 0

 ) {



 pkg.included_tests.forEach(test_row => {



 if (!test_row.linked_package)

 return;



 let child =

 frappe.model.add_child(

 new_doc,

 'results_table'

 );



 child.test_item =

 test_row.linked_package;



 });



 }



 // ✅ NO INCLUDED TESTS

 else {



 let child =

 frappe.model.add_child(

 new_doc,

 'results_table'

 );



 child.test_item =

 row.test_name;



 }



 }



 catch (e) {



 console.log(e);



 let child =

 frappe.model.add_child(

 new_doc,

 'results_table'

 );



 child.test_item =

 row.test_name;



 }

 }



 // =========================

 // CROPS

 // =========================

 if (

 frm.doc.crops_list &&

 frm.doc.crops_list.length > 0

 ) {



 frm.doc.crops_list.forEach(row => {



 let child =

 frappe.model.add_child(

 new_doc,

 'recommendations_table'

 );



 child.crop =

 row.crop_name;



 });

 }



 // =========================

 // OPEN FORM

 // =========================

 frappe.set_route(

 'Form',

 'Soil Test Result',

 new_doc.name

 );

}