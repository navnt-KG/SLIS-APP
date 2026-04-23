// // Copyright (c) 2026, navaneeth and contributors
// // For license information, please see license.txt

// frappe.query_reports["Sample Status"] = {
// 	"filters": [

// 	]
// };







frappe.query_reports["Your Report Name"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        }
    ]
};