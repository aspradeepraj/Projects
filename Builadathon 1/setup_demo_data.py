import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sow_pdf(filename="sow_contract.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    text = c.beginText(40, height - 50)
    text.setFont("Helvetica-Bold", 16)
    text.textLine("STATEMENT OF WORK: CORE BANKING CLOUD MIGRATION - WAVE 2")
    text.setFont("Helvetica", 11)
    text.textLine("")
    
    clauses = [
        "Section 4.2: Scope Creep Limits. Unapproved additions to functional specifications shall not exceed 5.0% of baseline story points without formal steering committee authorization and signed change orders.",
        "Section 7.1: Financial Milestone Thresholds. Milestone 3 budget burn rate shall not exceed 80.0% of allocated phase budget at the 50% completion checkpoint. Breaching this triggers immediate audit review.",
        "Section 9.4: Delivery Velocity SLAs. Sprint velocity variance shall not degrade by more than -20.0% across two consecutive reporting cycles. Violations incur vendor remediation penalties."
    ]
    
    for clause in clauses:
        text.textLines(clause)
        text.textLine("")
        
    c.drawText(text)
    c.save()
    print(f"Generated {filename}")

def create_raid_csv(filename="raid_log.csv"):
    data = {
        "ID": ["R01", "A01", "I01", "D01"],
        "Type": ["Risk", "Assumption", "Issue", "Dependency"],
        "Description": [
            "Legacy API rate limits causing pipeline latency",
            "Cloud infrastructure provisioned by client team on schedule",
            "Key architect resignation impacting sprint delivery velocity",
            "Third-party payment gateway certification pending compliance review"
        ],
        "Severity": ["High", "Medium", "Critical", "High"],
        "Owner": ["Vendor DevOps", "Client PM", "Vendor Delivery", "Compliance Lead"]
    }
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_sow_pdf()
    create_raid_csv()
    print("Demo data setup complete.")