// Copyright (c) 2026, navaneeth and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Result Entry", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Bulk Result Entry", {

    async refresh(frm) {
        if (!frm.selected_test) {
        frm.selected_test = "All";
    }

        await render_table(frm);

        frm.fields_dict.html.$wrapper
            .off("input")
            .on("input", ".cell", function () {

                let sample = $(this).data("sample");
                let test = $(this).data("test");
                let value = $(this).val();
                let key = $(this).data("key");


                update_json(
                    frm,
                    sample,
                    test,
                    key,
                    value
                );

            });
        frm.fields_dict.html.$wrapper
            .off("change", ".machine-select")
            .on(
                "change",
                ".machine-select",
                function () {

                    update_machine_for_test(
                        frm,
                        frm.selected_test,
                        $(this).val()
                    );
                }
            );    
        
       

        frm.fields_dict.html.$wrapper
            .off("click", ".test-filter")
            .on("click", ".test-filter", async function () {

                frm.selected_test =
                    $(this).data("test");

                await render_table(frm);
            });
    },
    async after_save(frm) {
        await render_table(frm);
    }
});


// =====================================
// HTML TABLE
// =====================================

async function render_table(frm) {
    let rows = frm.doc.sample_data || [];

    let tests = [];

    let selected_test =
        frm.selected_test || "All";
    let package_doc = null;
    if (!frm.test_packages) {
    frm.test_packages = {};
}
    if (selected_test !== "All") {

        try {

            package_doc =
                await frappe.db.get_doc(
                    "Soil Test Package",
                    selected_test
                );
            frm.test_packages[selected_test] =
                package_doc;


            console.log(
                "PACKAGE DOC",
                package_doc
            );

            console.log(
                "FORMULA",
                package_doc.formula
            );

            console.log(
                "VARIABLE TABLE",
                package_doc.variable_table
            );

        } catch (e) {

            console.error(
                "PACKAGE ERROR",
                e
            );
        }
    }

    if (rows.length > 0) {

        try {

            let obj = JSON.parse(
                rows[0].values_json || "{}"
            );

            tests = Object.keys(obj);

        } catch (e) {
            console.error(e);
        }
    }
    let devices = [];

    try {
        devices = await frappe.db.get_list(
            "Asset",
            {
                filters: {
                    asset_category: "Devices"
                },
                fields: [
                    "name",
                    "asset_name"
                ],
                limit: 500
            }
        );
    } catch (e) {
        console.log(e);
    }
    let html = `
        <div style="margin-bottom:10px;">

            <button
                class="test-filter btn btn-xs ${
                    selected_test === "All"
                        ? "btn-primary"
                        : "btn-default"
                }"
                data-test="All">
                All
            </button>
    `;

    tests.forEach(test => {

        html += `
            <button
                class="test-filter btn btn-xs ${
                    selected_test === test
                        ? "btn-primary"
                        : "btn-default"
                }"
                data-test="${test}"
                style="margin-left:5px;">
                ${test}
            </button>
        `;
    });
    let selected_machine = "";

    if (rows.length > 0) {
        try {
            let first_obj = JSON.parse(
                rows[0].values_json || "{}"
            );

            if (
                first_obj[selected_test] &&
                typeof first_obj[selected_test] === "object"
            ) {
                selected_machine =
                    first_obj[selected_test].machine || "";
            }
        } catch (e) {}
    }



       
    if (selected_test !== "All") {

        html += `
            <div style="margin-bottom:15px;">
                <label><b>Machine Name</b></label>

                <select
                    class="machine-select form-control"
                    style="width:300px;"
                >

                    <option value="">
                        Select Machine
                    </option>
        `;

        devices.forEach(d => {

            html += `
                <option
                    value="${d.asset_name}"
                    ${
                        selected_machine === d.asset_name
                            ? "selected"
                            : ""
                    }
                >
                    ${d.asset_name}
                </option>
            `;
        });

        html += `
                </select>
            </div>
        `;
    }

    html += `
        </div>

        <div style="overflow:auto;">
        <table class="table table-bordered table-sm">

        <thead>
            <tr>
                <th>Sample ID</th>
                <th>Lab Code</th>
    `;
    if (selected_test !== "All") {
        html += `<th>Machine Name</th>`;
    }

    if (selected_test === "All") {

        tests.forEach(test => {

            html += `
                <th>${test}</th>
            `;
        });

    }
    else if (package_doc) {

        package_doc.variable_table.forEach(v => {

            html += `
                <th>${v.label}</th>
            `;
        });

        html += `
            <th>Formula</th>
            <th>${selected_test}</th>
        `;
    }

    html += `
            </tr>
        </thead>

        <tbody>
    `;

    rows.forEach(row => {

        let sample_id =
            row.sample_id ||
            row.variant_reference ||
            "";

        let obj = {};

        try {

            obj = JSON.parse(
                row.values_json || "{}"
            );
            console.log("ROW JSON =", row.values_json);
            console.log("OBJ =", obj);

        } catch (e) {
            console.error(e);
        }

        html += `
            <tr>

                <td>
                    ${sample_id}
                </td>

                <td>
                    ${row.lab_code || ""}
                </td>
        `;
        if (selected_test !== "All") {

            html += `
                <td>
                    ${selected_machine}
                </td>
            `;
        }

        if (
            selected_test !== "All" &&
            package_doc
        ) {

            package_doc.variable_table.forEach(v => {

                html += `
                    <td>
                        <input
                            type="number"
                            class="cell form-control variable-input"
                            data-sample="${sample_id}"
                            data-test="${selected_test}"
                            data-key="${v.variable_key}"
                            value="${
                                obj[selected_test]?.[v.variable_key]
                                ?? v.default_value
                                ?? ''
                            }"
                        >
                    </td>
                `;
            });

            let result = 0;

            try {

                let formula =
                    package_doc.formula || "";

                package_doc.variable_table.forEach(v => {

                    let val =
                        obj[selected_test]?.[
                            v.variable_key
                        ]
                        ?? v.default_value
                        ?? 0;

                    formula =
                        formula.replaceAll(
                            v.variable_key,
                            val
                        );
                });

                result = eval(formula);
                if (!obj[selected_test]) {
                    obj[selected_test] = {};
                }

                obj[selected_test].result = result;
                frappe.model.set_value(
                row.doctype,
                row.name,
                "values_json",
                JSON.stringify(obj)
            );

            } catch (e) {

                console.log(e);
            }

            html += `
                <td>
                    ${package_doc.formula || ""}
                </td>

                <td class="final-value">
                    ${result}
                </td>
            `;
        }
        else {

            tests.forEach(test => {

                let value = 0;

                if (
                    typeof obj[test] === "object"
                ) {

                    value =
                        obj[test].result || 0;

                } else {

                    value =
                        obj[test] || 0;
                }

                html += `
                    <td>
                        ${value}
                    </td>
                `;
            });
        }

        html += `
            </tr>
        `;
    });

    html += `
        </tbody>
        </table>
        </div>
    `;

    frm.fields_dict.html.$wrapper.html(
        html
    );
}


// =====================================
// SAVE TO values_json
// =====================================

function update_json(
    frm,
    sample,
    test,
    key,
    value
) {

    (frm.doc.sample_data || []).forEach(row => {

        let row_sample =
            row.sample_id ||
            row.variant_reference ||
            "";

        if (
            row_sample == sample
        ) {

            let obj = {};

            try {

                obj = JSON.parse(
                    row.values_json || "{}"
                );

            } catch (e) {
                console.error(e);
            }

            if (typeof obj[test] !== "object") {

                obj[test] = {
                    machine: ""
                };
            }

            obj[test][key] =
                parseFloat(value) || 0;
            
            

            let formula = "";

            if (
                frm.test_packages &&
                frm.test_packages[test]
            ) {

                formula =
                    frm.test_packages[test].formula || "";
            }

            if (formula) {

                Object.keys(obj[test]).forEach(k => {

                    if (
                        k !== "machine" &&
                        k !== "result"
                    ) {

                        formula =
                            formula.replaceAll(
                                k,
                                obj[test][k]
                            );
                    }
                });

                try {

                    obj[test].result =
                        eval(formula);

                } catch (e) {

                    obj[test].result = 0;
                }
            }
            frappe.model.set_value(
                row.doctype,
                row.name,
                "values_json",
                JSON.stringify(obj)
            );

        }
    });


    

    frm.dirty();
}
    function update_machine_for_test(
        frm,
        test,
        machine
    ) {

        (frm.doc.sample_data || [])
        .forEach(row => {

            let obj = {};

            try {

                obj = JSON.parse(
                    row.values_json || "{}"
                );

            } catch (e) {}

            if (
                typeof obj[test] !== "object"
            ) {

                obj[test] = {
                    machine: ""
                };
            }
            obj[test].machine =
                machine;

            frappe.model.set_value(
                row.doctype,
                row.name,
                "values_json",
                JSON.stringify(obj)
            );
        });

        frm.dirty();

        frm.trigger("refresh");
    }