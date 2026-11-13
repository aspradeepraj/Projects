import os
import pandas as pd
from fpdf import FPDF
from PIL import Image

os.makedirs("data", exist_ok=True)
os.makedirs("assets", exist_ok=True)

LOGO_PATH = "assets/social_eagle_logo.png"
CLEAN_LOGO_PATH = "assets/social_eagle_clean.png"


def prepare_logo():
    if not os.path.exists(LOGO_PATH):
        return None
    img = Image.open(LOGO_PATH).convert("RGBA")
    w, h = img.size
    cropped = img.crop((int(w * 0.02), int(h * 0.05), int(w * 0.99), int(h * 0.95)))
    cropped.save(CLEAN_LOGO_PATH)
    return CLEAN_LOGO_PATH


class EnterpriseSOWPDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        with self.local_context(fill_opacity=0.06):
            self.set_font("Helvetica", "B", 44)
            self.set_text_color(180, 30, 30)
            with self.rotation(angle=35, x=105, y=155):
                self.text(28, 155, "SOCIAL EAGLE CONFIDENTIAL")

        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=12, y=8, w=58)
        else:
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(180, 30, 30)
            self.set_xy(12, 10)
            self.cell(60, 10, "SOCIAL EAGLE | together we rise")

        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(70, 70, 70)
        self.set_xy(115, 9)
        self.cell(83, 4.5, "MASTER STATEMENT OF WORK (SOW)", align="R", ln=True)
        self.set_x(115)
        self.cell(83, 4.5, "Contract Ref: SE-SOW-2026-CB02", align="R", ln=True)
        self.set_x(115)
        self.cell(83, 4.5, "Classification: RESTRICTED - GOVERNANCE AUDIT", align="R", ln=True)

        self.set_draw_color(180, 30, 30)
        self.set_line_width(0.8)
        self.line(12, 26, 198, 26)
        self.ln(8)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(12, 280, 198, 280)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(120, 8, "Social Eagle Enterprise Delivery Governance | Together We Rise", align="L")
        self.cell(66, 8, f"Page {self.page_no()} of {{nb}}", align="R")

    def section_banner(self, title):
        self.set_fill_color(165, 28, 36)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10.5)
        self.cell(0, 8, f"  {title}", ln=True, fill=True)
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def body_paragraph(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(35, 35, 35)
        self.set_x(self.l_margin); self.multi_cell(0, 5.5, text)
        self.ln(3)

    def clause_callout(self, clause_id, text):
        self.set_fill_color(250, 242, 242)
        self.set_draw_color(180, 30, 30)
        self.set_line_width(0.5)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(150, 20, 25)
        self.set_x(self.l_margin); self.multi_cell(0, 6, f" {clause_id}", border="LTR", fill=True)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(30, 30, 30)
        self.set_x(self.l_margin); self.multi_cell(0, 5.5, f" {text}", border="LBR", fill=True)
        self.ln(4)

    def styled_table(self, headers, rows, col_widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(35, 42, 54)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7.5, f" {h}", border=1, fill=True)
        self.ln()

        self.set_font("Helvetica", "", 8.8)
        self.set_text_color(30, 30, 30)
        for idx, row in enumerate(rows):
            fill = idx % 2 == 1
            self.set_fill_color(245, 247, 250) if fill else self.set_fill_color(255, 255, 255)
            for val, w in zip(row, col_widths):
                self.cell(w, 7, f" {val}", border=1, fill=True)
            self.ln()
        self.ln(4)


def generate_rich_sow():
    clean_logo = prepare_logo()
    pdf = EnterpriseSOWPDF(logo_path=clean_logo)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # PAGE 1
    pdf.add_page()
    pdf.section_banner("1. EXECUTIVE PROGRAM CHARTER & CONTRACT METADATA")
    pdf.body_paragraph(
        "This Master Statement of Work ('SOW') is executed between Social Eagle Enterprise Delivery "
        "('Delivery Partner') and Global FinCorp Holdings ('Client') for the Core Banking Cloud Migration - Wave 2 "
        "engagement. All engineering sprints, cloud infrastructure provisioning, security gates, and vendor "
        "status disclosures are governed by the automated audit thresholds defined herein."
    )

    pdf.styled_table(
        headers=["Contract Attribute", "Binding Specification"],
        rows=[
            ["Program Title", "Core Banking Cloud Migration - Wave 2 (PRG-2026-CB02)"],
            ["Contractual Model", "Fixed-Capacity Agile Pods with Milestone SLA Holdbacks"],
            ["Total Approved Budget", "$4,200,000 USD (Waves 1 through 3 Cumulative Cap)"],
            ["Governance Oversight", "Social Eagle PMO & Autonomous GovGuard AI Audit Engine"],
            ["Compliance Standards", "ISO/IEC 27001, SOC 2 Type II, PCI-DSS v4.0, Agile PMO v3"],
            ["Reporting Cadence", "Bi-Weekly Sprint Telemetry + Continuous Legacy Portal Sync"],
            ["Effective Period", "January 15, 2026 - December 20, 2026"],
        ],
        col_widths=(65, 121),
    )

    pdf.section_banner("2. MILESTONE DELIVERABLES & FINANCIAL ALLOCATION SCHEDULE")
    pdf.body_paragraph(
        "Capital disbursement and resource burn are tied directly to verified milestone exit criteria. "
        "Expenditures exceeding milestone caps require prior written authorization from the Steering Committee."
    )

    pdf.styled_table(
        headers=["Milestone", "Scope Deliverable", "Target Date", "Budget Cap", "Burn Alert Gate"],
        rows=[
            ["Milestone 1", "Core Ledger Schema & VPC Landing Zone", "Mar 30, 2026", "$1,200,000", "28.5% Cumulative"],
            ["Milestone 2", "Payment Rail APIs & UAT Readiness", "Jul 15, 2026", "$1,680,000", "68.5% Cumulative"],
            ["Milestone 3", "Parallel Run & Production Cutover", "Nov 30, 2026", "$1,320,000", "80.0% Hard Ceiling"],
        ],
        col_widths=(28, 66, 30, 30, 32),
    )

    pdf.clause_callout(
        "CLAUSE 7.1 - BUDGET BURN THRESHOLD & FINANCIAL FREEZE",
        "If cumulative program budget burn exceeds 80.0% prior to formal Client sign-off of Milestone 3 "
        "(Production Cutover), an immediate Executive Steering Committee Escalation and non-essential "
        "expenditure freeze are mandatory within 48 hours.",
    )

    # PAGE 2
    pdf.add_page()
    pdf.section_banner("3. SCOPE MANAGEMENT, CHANGE CONTROL & VELOCITY SLAs")
    pdf.body_paragraph(
        "To eliminate silent backlog inflation and unbilled engineering effort, every user story pulled into "
        "an active sprint must trace back to the baselined Milestone 2 Product Backlog."
    )

    pdf.clause_callout(
        "CLAUSE 4.2 - SCOPE CREEP & CHANGE REQUEST (CR) CEILING",
        "Any unapproved scope addition or backlog expansion exceeding 5.0% of baseline sprint story points "
        "requires a formally signed Change Request (CR) approved by the Enterprise Architecture Board prior to "
        "sprint execution. Executing unapproved scope above 5.0% constitutes an immediate Contractual Breach.",
    )

    pdf.clause_callout(
        "CLAUSE 9.4 - SPRINT VELOCITY VARIANCE & RECOVERY PLAN",
        "Delivery pods must maintain rolling sprint velocity within +/- 15.0% of the 3-sprint baseline average. "
        "Any negative sprint velocity variance greater than 20.0% (worse than -20.0%) across two consecutive "
        "sprints automatically triggers a mandatory Delivery Recovery Plan and 10% invoice holdback review.",
    )

    pdf.section_banner("4. GOVERNANCE RACI MATRIX & ESCALATION PROTOCOL")
    pdf.styled_table(
        headers=["Governance Activity", "Social Eagle PM", "Tech Architect", "Client VP", "GovGuard AI"],
        rows=[
            ["Daily Sprint & Burn Telemetry", "Responsible", "Consulted", "Informed", "Accountable"],
            ["Change Request (>5% Scope)", "Responsible", "Accountable", "Approver", "Auditor"],
            ["Budget Overrun (>80% Cap)", "Consulted", "Informed", "Approver", "Escalator"],
            ["RAG Status Integrity Audit", "Responsible", "Consulted", "Informed", "Accountable"],
        ],
        col_widths=(62, 31, 31, 31, 31),
    )

    # PAGE 3
    pdf.add_page()
    pdf.section_banner("5. STATUS REPORTING INTEGRITY & AUDIT COMPLIANCE")
    pdf.body_paragraph(
        "Vendor self-certification on internal PMO trackers is subject to automated cross-verification against "
        "Jira sprint logs, cloud billing exports, and contractual SLA thresholds."
    )

    pdf.clause_callout(
        "CLAUSE 11.3 - MATERIAL GOVERNANCE MISREPORTING EVENT",
        "Marking an overall program status as GREEN on internal PMO portals while breaching any threshold "
        "defined in Clause 4.2 (Scope > 5%), Clause 7.1 (Budget Burn > 80%), or Clause 9.4 (Velocity Variance "
        "< -20%) is classified as a Material Governance Misreporting Event requiring immediate VP escalation.",
    )

    pdf.section_banner("6. KEY SLA THRESHOLD SUMMARY TABLE (RAG ENGINE REFERENCE)")
    pdf.styled_table(
        headers=["Metric ID", "Governance KPI", "Green Zone", "Amber Zone", "Red Breach Trigger"],
        rows=[
            ["KPI-01", "Cumulative Budget Burn", "< 70.0%", "70.0% - 80.0%", "> 80.0% before M3"],
            ["KPI-02", "Unapproved Scope Creep", "0.0% - 2.5%", "2.6% - 5.0%", "> 5.0% without CR"],
            ["KPI-03", "Sprint Velocity Variance", "+/- 15.0%", "-15.1% to -20.0%", "Worse than -20.0%"],
            ["KPI-04", "Portal Status Alignment", "100% Match", "Minor Lag", "False GREEN Status"],
        ],col_widths=(24, 52, 34, 38, 38),
)
    pdf.section_banner("7. FINANCIAL PENALTIES, SLA HOLDBACKS & ESCALATION TIERS")
    pdf.styled_table(
headers=["Breach Severity", "Trigger Condition", "Commercial Penalty / Holdback", "Escalation SLA"],
rows=[
["Tier 1 - Critical", "False GREEN + >=2 SLA Breaches", "15% Milestone Holdback + Audit", "Immediate (< 4 hrs)"],
["Tier 2 - High", "Budget > 80% OR Scope > 5%", "10% Invoice Holdback + Freeze", "Within 24 Hours"],
["Tier 3 - Moderate", "Velocity Variance < -20%", "Mandatory Recovery Plan (DRP)", "Within 48 Hours"],
],
col_widths=(34, 56, 58, 38),
)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(93, 6, "Authorized for Social Eagle:", border="T")
    pdf.cell(93, 6, "Accepted by Enterprise Client:", border="T", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(93, 5, "Director of Program Governance | Social Eagle")
    pdf.cell(93, 5, "VP of Core Banking Transformation", ln=True)
    pdf.output("data/sow_contract.pdf")
    print("Generated branded 3-page data/sow_contract.pdf with watermark, logo & tables!")
if __name__ == "__main__":
    generate_rich_sow()
    raid_data = [
    {"ID": "RSK-01", "Type": "Risk", "Description": "Core ledger API latency exceeding 400ms in UAT", "Owner": "Lead Architect", "Severity": "High", "Status": "Open"},
    {"ID": "ISS-04", "Type": "Issue", "Description": "11.2% unapproved features added to Sprint 14 without signed CR", "Owner": "Vendor PM", "Severity": "Critical", "Status": "Escalated"},
    {"ID": "DEP-02", "Type": "Dependency", "Description": "InfoSec penetration testing sign-off delayed by 6 days", "Owner": "Security Team", "Severity": "Medium", "Status": "In Progress"},
    ]
    pd.DataFrame(raid_data).to_csv("data/raid_log.csv", index=False)
    print("Generated data/raid_log.csv")
