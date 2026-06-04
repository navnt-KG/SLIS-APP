// Copyright (c) 2026, navaneeth and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Result Entry", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Bulk Result Entry", {

    refresh(frm) {
        if (!frm.selected_test) {
        frm.selected_test = "All";
    }

        render_table(frm);

        frm.fields_dict.html.$wrapper
            .off("input")
            .on("input", ".cell", function () {

                let sample = $(this).data("sample");
                let test = $(this).data("test");
                let value = $(this).val();

                update_json(
                    frm,
                    sample,
                    test,
                    value
                );

            });

        frm.fields_dict.html.$wrapper
            .off("click", ".test-filter")
            .on("click", ".test-filter", function () {

                frm.selected_test =
                    $(this).data("test");

                render_table(frm);
            });
    },
    after_save(frm) {
        render_table(frm);
    }
});


// =====================================
// HTML TABLE
// =====================================

function render_table(frm) {

    let rows = frm.doc.sample_data || [];

    let tests = [];

    let selected_test =
        frm.selected_test || "All";

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

    html += `
        </div>

        <div style="overflow:auto;">
        <table class="table table-bordered table-sm">

        <thead>
            <tr>
                <th>Sample ID</th>
                <th>Lab Code</th>
    `;

    tests
        .filter(test =>
            selected_test === "All" ||
            test === selected_test
        )
        .forEach(test => {

            html += `
                <th>${test}</th>
            `;
        });

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

        tests
            .filter(test =>
                selected_test === "All" ||
                test === selected_test
            )
            .forEach(test => {

                html += `
                    <td>

                        <input
                            type="text"

                            class="cell form-control ${
                                obj[test]
                                    ? "bg-success text-dark"
                                    : ""
                            }"

                            data-sample="${sample_id}"

                            data-test="${test}"

                            value="${String(obj[test] ?? '')}"
                        >

                    </td>
                `;
            });

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

            obj[test] = value;

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