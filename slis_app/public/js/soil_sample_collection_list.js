// console.log("SOIL SAMPLE LIST JS LOADED");

// setInterval(() => {ved

//     if (
//         !cur_list ||
//         cur_list.doctype !==
//         "Soil Sample Collection"
//     ) {
//         return;
//     }

//     // BUTTON ALREADY EXISTS

//     if (
//         $(".custom-move-test-btn")
//         .length
//     ) {
//         return;
//     }

//     console.log("ADDING BUTTON");

//     let button =
//         cur_list.page.add_inner_button(

//             __("Move to Test"),

//             function () {

//                 frappe.msgprint(
//                     "Button Working"
//                 );
//             }
//         );

//     $(button).addClass(
//         "custom-move-test-btn"
//     );

//     console.log("BUTTON ADDED");

// }, 2000);



console.log("SOIL SAMPLE LIST JS LOADED");

setInterval(() => {

    if (
        !cur_list ||
        cur_list.doctype !==
        "Soil Sample Collection"
    ) {
        return;
    }

    // BUTTON ALREADY EXISTS

    if (
        $(".custom-move-test-btn")
        .length
    ) {
        return;
    }

    console.log("ADDING BUTTON");

    let button =
        cur_list.page.add_inner_button(

            __("Move to Test"),

            async function () {

                console.log("BUTTON CLICKED");
                

                let selected =
                    cur_list.get_checked_items();

                if (
                    !selected ||
                    selected.length === 0
                ) {

                    frappe.msgprint(
                        "Please select at least one sample"
                    );

                    return;
                }

                

                

                // =====================================
                // FETCH FULL DOCS
                // =====================================

                let children_docs = [];
                window.last_selected_samples = [];

                for (let item of selected) {

                    let doc =
                        await frappe.db.get_doc(
                            "Soil Sample Collection",
                            item.name
                        );

                    children_docs.push(doc);
                }

      

                // =====================================
                // GROUP BY PARENT
                // =====================================

                let parent_map = {};

                for (let doc of children_docs) {

                    let parent_name =
                        doc.parent_sample || doc.name;

                    if (!parent_map[parent_name]) {

                        parent_map[parent_name] = [];
                    }

                    parent_map[parent_name].push(doc);
                }
   
                // =====================================
                // PROCESS EACH PARENT
                // =====================================
                let valid_count = 0;

                for (let item of selected) {

                    let doc = await frappe.db.get_doc(
                        "Soil Sample Collection",
                        item.name
                    );

                    valid_count++;
                }

                

                
                let moved_count = 0;
                let done = 0;

                for (
                    let parent_name of
                    Object.keys(parent_map)
                ) {

                    let child_docs =
                        parent_map[parent_name];

                    let parent_doc =
                        await frappe.db.get_doc(
                            "Soil Sample Collection",
                            parent_name
                        );

                   

                    // =====================================
                    // SAVE SELECTED SAMPLES
                    // =====================================

                   

                    selected.forEach(row => {

                        let row_name = row.name;

                        // Parent skip cheyyuka
                        if (row_name === parent_name) {
                            return;
                        }

                        if (
                            !window.last_selected_samples.includes(
                                row_name
                            )
                        ) {

                            window.last_selected_samples.push(
                                row_name
                            );
                        }
                    });

                    // Single sample case
                    if (
                        window.last_selected_samples.length === 0 &&
                        selected.length === 1
                    ) {

                        window.last_selected_samples.push(
                            parent_name
                        );
                    }

                    if (parent_doc.moved_to_test == 1) {

                        let proceed =
                            await new Promise(resolve => {

                                frappe.confirm(
                                    `${parent_name} is already moved to test.<br><br>Do you want to update the existing test result?`,
                                    () => resolve(true),
                                    () => resolve(false)
                                );
                            });

                        if (!proceed) {

                            frappe.show_alert({
                                message: `${parent_name} skipped`,
                                indicator: "orange"
                            });

                            continue;
                        }
                    }
                    if (done === 0) {
                        frappe.show_progress(
                            "Moving to Test...",
                            0,
                            valid_count
                        );
                    }
                                                                            
                    // CHECK EXISTING TEST RESULT
                    // =====================================

                    let existing_list =
                        await frappe.db.get_list(
                            "Soil Test Result",
                            {
                                filters: {
                                    main_sample_id:
                                        parent_name
                                },

                                fields: ["name"],

                                limit: 1
                            }
                        );

                    let test_result_doc;

                    // =====================================
                    // EXISTING RESULT
                    // =====================================

                    if (
                        existing_list &&
                        existing_list.length > 0
                    ) { 

                        // =====================================
                        // LOAD EXISTING DOC
                        // =====================================

                        test_result_doc =
                            await frappe.db.get_doc(
                                "Soil Test Result",
                                existing_list[0].name
                            );

                        // =====================================
                        // CLEAR OLD DATA
                        // =====================================

                        test_result_doc
                            .test_sample_data = [];

                        frappe.show_alert({

                            message:
                                `${parent_name} existing data updated`,

                            indicator:
                                "blue"
                        });

                    } else {

                        // =====================================
                        // CREATE NEW TEST RESULT
                        // =====================================

                        await frappe.model.with_doctype(
                            "Soil Test Result"
                        );

                        test_result_doc =
                            frappe.model.get_new_doc(
                                "Soil Test Result"
                            );

                        // BASIC FIELDS

                        test_result_doc.main_sample_id =
                            parent_name;

                        test_result_doc.client =
                            parent_doc.client;

                        test_result_doc.client_type =
                            parent_doc.client_type;

                        test_result_doc.latitude =
                            parent_doc.latitude;

                        test_result_doc.longitude =
                            parent_doc.longitude;

                        test_result_doc.plot_size =
                            parent_doc.plot_size;

                        test_result_doc.name_of_type =
                            parent_doc.name_of_type;

                        test_result_doc.type_of_collection =
                            parent_doc.type_of_collection;

                        test_result_doc.number_of_sample =
                            parent_doc.number_of_samples;

                        test_result_doc.lab_code_prefix =
                            parent_doc.lab_code_prefix;

                        test_result_doc.lab_code_start =
                            parent_doc.lab_code_start;

                        test_result_doc.test_sample_data = [];
                    }

                    // =====================================
                    // EXISTING SAMPLE IDS
                    // =====================================

                    let existing_sample_ids =
                        (
                            test_result_doc
                            .test_sample_data || []
                        ).map(
                            r => r.sample_id
                        );

                    // =====================================
                    // CLIENT TYPE
                    // =====================================

                    let is_consultancy =
                        (
                            parent_doc.client_type || ""
                        ) === "Consultancy";

                    let is_farmer =
                        (
                            parent_doc.client_type || ""
                        ) === "Farmer";

                    // =====================================
                    // LOOP CHILD DOCS
                    // =====================================

                    for (
                        let child_doc of child_docs
                    ) {

                        let ref_id =
                            child_doc
                            .reference_sample_id || "";

                        // =====================================
                        // FARMER
                        // =====================================

                        if (is_farmer) {
                            console.log("SAMPLE DATA =", child_doc.sample_data);

                            if (
                                existing_sample_ids.includes(
                                    child_doc.name
                                )
                            ) continue;

                            if (
                                !test_result_doc.test_sample_data
                            ) {

                                test_result_doc.test_sample_data = [];
                            }

                            let farmer_row =
                                (child_doc.sample_data || [])[0];
                            console.log("FARMER ROW =", farmer_row);
                            test_result_doc.test_sample_data.push({

                                sample_id:
                                    farmer_row?.sample_id || child_doc.name,

                                lab_code:
                                    farmer_row?.lab_code || "",

                                values_json:
                                    farmer_row?.values_json || "{}"
                            });

                            existing_sample_ids.push(
                                child_doc.name
                            );

                            continue;
                        }
                        // =====================================
                        // DEPARTMENT / CONSULTANCY
                        // =====================================

                        let matched_row =
                            (
                                parent_doc.sample_data || []
                            ).find(
                                r =>
                                r.sample_id === ref_id
                            );

                        if (!matched_row)
                            continue;

                        let row_sample_id =
                            is_consultancy
                                ? matched_row.lab_code
                                : matched_row.sample_id;

                        // SKIP DUPLICATE

                        if (
                            existing_sample_ids.includes(
                                row_sample_id
                            )
                        ) continue;

                        if (
                            !test_result_doc
                            .test_sample_data
                        ) {

                            test_result_doc
                                .test_sample_data = [];
                        }

                        test_result_doc
                            .test_sample_data.push({

                                sample_id:
                                    row_sample_id,

                                lab_code:
                                    matched_row.lab_code,

                                values_json:
                                    matched_row.values_json || "{}"
                            });

                        existing_sample_ids.push(
                            row_sample_id
                        );
                    }

                    // =====================================
                    // SAVE / INSERT
                    // =====================================

                    if (
                        existing_list &&
                        existing_list.length > 0
                    ) {

                        await frappe.call({

                            method:
                                "frappe.client.save",

                            args: {
                                doc:
                                    test_result_doc
                            }
                        });

                        frappe.show_alert({

                            message:
                                "Soil Test Result Updated",

                            indicator:
                                "green"
                        });

                    } else {

                        await frappe.call({

                            method:
                                "frappe.client.insert",

                            args: {
                                doc:
                                    test_result_doc
                            }
                        });

                        frappe.show_alert({

                            message:
                                "Soil Test Result Created",

                            indicator:
                                "green"
                        });
                    }

                    // =====================================
                    // UPDATE STATUS
                    // =====================================
                    for (let child_doc of child_docs) {

                        await frappe.db.set_value(
                            "Soil Sample Collection",
                            child_doc.name,
                            {
                                status: "With Research Assistant",
                                moved_to_test: 1,
                                lab_name: parent_doc.target_lab
                            }
                        );
                    }
                    await frappe.db.set_value(
                        "Soil Sample Collection",
                        parent_name,
                        {
                            status: "With Research Assistant",
                            moved_to_test: 1,
                            lab_name: parent_doc.target_lab
                        }
                    );
                    frappe.show_alert({
                        message: `${parent_name} moved to test successfully`,
                        indicator: "green"
                    });
                    moved_count++;

                    done += child_docs.length;

                    frappe.show_progress(
                        "Moving to Test...",
                        done,
                        valid_count
                    );
                }

               frappe.hide_progress();

                if (moved_count > 0) {

                    frappe.msgprint({
                        title: __("Move To Test Completed"),
                        indicator: "green",
                        message: `${moved_count} sample(s) moved successfully`
                    });
                    

                }
                

                cur_list.refresh();

                setTimeout(() => {

                    if (window.last_selected_samples) {

                        window.last_selected_samples.forEach(name => {

                            cur_list.$result
                                .find(`input[data-name="${name}"]`)
                                .prop("checked", true)
                                .trigger("change");
                        });
                    }

                }, 2500);
            }
        );

        $(button).addClass(
        "custom-move-test-btn"
    );

    // =====================================
    // BULK RESULT ENTRY BUTTON
    // =====================================

    if (!$(".custom-bulk-result-btn").length) {

        let bulk_button =
            cur_list.page.add_inner_button(

                __("Bulk Result Entry"),

                async function () {

                    let selected =
                        cur_list.get_checked_items();

                    if (
                        (!selected || selected.length === 0) &&
                        window.last_selected_samples
                    ) {
                        selected =
                            window.last_selected_samples.map(
                                name => ({ name })
                            );
                    }

                    if (!selected || selected.length === 0) {
                        frappe.msgprint(
                            "Please select at least one sample"
                        );
                        return;
                    }

                    await frappe.model.with_doctype(
                        "Bulk Result Entry"
                    );

                    let bulk_doc =
                        frappe.model.get_new_doc(
                            "Bulk Result Entry"
                        );

                    bulk_doc.sample_data = [];

                    for (let item of selected) {

                        let doc =
                            await frappe.db.get_doc(
                                "Soil Sample Collection",
                                item.name
                            );
                        // Farmer => Parent only
                        if (
                            doc.client_type === "Farmer" &&
                            doc.parent_sample
                        ) {
                            continue;
                        }

                        if (!doc.verified_physical_sample) {

                            frappe.msgprint(
                                `${doc.name} : Verified Physical Sample must be checked`
                            );

                            return;
                        }

                        if (!doc.moved_to_test) {

                            frappe.msgprint(
                                `${doc.name} : Please click Move To Test first`
                            );

                            return;
                        }

                        if (
                            doc.status !==
                            "With Research Assistant"
                        ) {

                            frappe.msgprint(
                                `${doc.name} : Status must be Research Assistant`
                            );

                            return;
                        }

                        
                        // Parent selected -> skip
                        // Parent with child samples -> skip
                        if (
                            doc.client_type !== "Farmer" &&
                            !doc.parent_sample &&
                            doc.sample_data &&
                            doc.sample_data.length > 1
                        ) {
                            continue;
                        }
                        let lab_code = doc.lab_code || "";

                        if (doc.parent_sample) {

                            let parent_doc =
                                await frappe.db.get_doc(
                                    "Soil Sample Collection",
                                    doc.parent_sample
                                );

                            let matched_row =
                                (parent_doc.sample_data || []).find(
                                    r =>
                                    r.sample_id ===
                                    doc.reference_sample_id
                                );

                            lab_code =
                                matched_row?.lab_code || "";
                        }

                        // Child only add
                        let values_json = "{}";

                        if (doc.parent_sample) {

                            let parent_doc =
                                await frappe.db.get_doc(
                                    "Soil Sample Collection",
                                    doc.parent_sample
                                );

                            let matched_row =
                                (parent_doc.sample_data || []).find(
                                    r =>
                                    r.sample_id ===
                                    doc.reference_sample_id
                                );

                            values_json =
                                matched_row?.values_json || "{}";
                        }
                        // Farmer
                        if (doc.client_type === "Farmer") {

                            let farmer_row =
                                (doc.sample_data || [])[0];

                            if (farmer_row) {

                                lab_code =
                                    farmer_row.lab_code || "";

                                values_json =
                                    farmer_row.values_json || "{}";
                            }
                        }

                        bulk_doc.sample_data.push({

                            sample_id:
                                doc.client_type === "Farmer"
                                    ? doc.name
                                    : doc.reference_sample_id,

                            variant_reference:
                                doc.client_type === "Farmer"
                                    ? doc.name
                                    : (doc.reference_sample_id || ""),

                            lab_code:
                                lab_code,

                            values_json:
                                values_json

                        });
                    }

                    frappe.set_route(
                        "Form",
                        "Bulk Result Entry",
                        bulk_doc.name
                    );

                                    } // end async function
                                ); // end add_inner_button

                            $(bulk_button).addClass(
                                "custom-bulk-result-btn"
                            );
                        }

                        // =====================================
                        // PARENT -> AUTO SELECT CHILDREN
                        // =====================================
                       
                        $(document).on(
                            "change",
                            "input[type='checkbox']",
                            async function () {

                                let checked =
                                    $(this).prop("checked");

                                let row_name =
                                    $(this)
                                    .closest('.list-row-container')
                                    .find('.list-subject a')
                                    .text()
                                    .trim();

                                if (!row_name) {
                                    return;
                                }

                                let doc =
                                    await frappe.db.get_doc(
                                        "Soil Sample Collection",
                                        row_name
                                    );

                                // Farmer skip
                                if (doc.client_type === "Farmer") {
                                    return;
                                }

                                // =====================================
                                // PARENT -> CHILDREN
                                // =====================================

                                if (!doc.parent_sample) {

                                    let children =
                                        await frappe.db.get_list(
                                            "Soil Sample Collection",
                                            {
                                                filters: {
                                                    parent_sample: doc.name
                                                },
                                                fields: ["name"]
                                            }
                                        );

                                    children.forEach(child => {

                                        $('.list-row-container').each(function () {

                                            let child_row_name =
                                                $(this)
                                                .find('.list-subject a')
                                                .text()
                                                .trim();

                                            if (
                                                child_row_name === child.name
                                            ) {

                                                $(this)
                                                    .find(
                                                        'input[type="checkbox"]'
                                                    )
                                                    .prop(
                                                        'checked',
                                                        checked
                                                    );
                                            }
                                        });

                                    });
                                }

                                // =====================================
                                // CHILD -> PARENT
                                // =====================================

                                else {

                                    let siblings =
                                        await frappe.db.get_list(
                                            "Soil Sample Collection",
                                            {
                                                filters: {
                                                    parent_sample:
                                                        doc.parent_sample
                                                },
                                                fields: ["name"]
                                            }
                                        );

                                    let all_checked = true;

                                    siblings.forEach(sibling => {

                                        $('.list-row-container').each(function () {

                                            let sibling_name =
                                                $(this)
                                                .find('.list-subject a')
                                                .text()
                                                .trim();

                                            if (
                                                sibling_name === sibling.name
                                            ) {

                                                let is_checked =
                                                    $(this)
                                                    .find(
                                                        'input[type="checkbox"]'
                                                    )
                                                    .prop("checked");

                                                if (!is_checked) {
                                                    all_checked = false;
                                                }
                                            }
                                        });

                                    });

                                    $('.list-row-container').each(function () {

                                        let parent_row_name =
                                            $(this)
                                            .find('.list-subject a')
                                            .text()
                                            .trim();

                                        if (
                                            parent_row_name ===
                                            doc.parent_sample
                                        ) {

                                            $(this)
                                                .find(
                                                    'input[type="checkbox"]'
                                                )
                                                .prop(
                                                    "checked",
                                                    all_checked
                                                );
                                        }
                                    });
                                }
                            }
                        );                                                                                                                                           
                        console.log("BUTTON ADDED");

                        }, 2000);