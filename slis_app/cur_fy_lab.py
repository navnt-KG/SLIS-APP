import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_lab_summary_fy():
    today = now_datetime()
    current_year = today.year
    
    # Financial Year Start Calculation
    if today.month >= 4:
        fy_start = f"{current_year}-04-01"
    else:
        fy_start = f"{current_year - 1}-04-01"

    # 1. Get all unique labs from the 'target_lab' field
    all_labs = frappe.get_all("Soil Sample Collection", fields=["distinct target_lab"])
    summary = {}
    for l in all_labs:
        name = l.target_lab or "Unassigned"
        summary[name] = {"pending": 0, "completed": 0, "total": 0}

    # 2. Fetch samples from this FY
    data = frappe.get_all("Soil Sample Collection", 
        filters={
            "creation": [">=", fy_start]
        },
        fields=["target_lab", "status"])

    # 3. Categorize counts
    for d in data:
        lab = d.target_lab or "Unassigned"
        if lab not in summary:
            summary[lab] = {"pending": 0, "completed": 0, "total": 0}
        
        # Match case to your DocType status options
        if d.status == "completed":
            summary[lab]["completed"] += 1
        elif d.status not in ["completed", "draft", "Cancelled"]:
            summary[lab]["pending"] += 1
            
        summary[lab]["total"] += 1

    # 4. Format for Table with Completion Status
    final_list = []
    for idx, (lab, counts) in enumerate(summary.items(), start=1):
        # Calculate completion percentage for the 'Status' column
        percentage = 0
        if counts["total"] > 0:
            percentage = round((counts["completed"] / counts["total"]) * 100, 1)
        
        final_list.append({
            "sn": idx,
            "lab": lab,
            "total": counts["total"],
            "pending": counts["pending"],
            "completed": counts["completed"],
            "status_pct": f"{percentage}%"
        })
    
    return final_list