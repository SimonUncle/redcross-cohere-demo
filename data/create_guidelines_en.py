"""English Blood Donation Screening Guidelines — 3 PDFs (reportlab)"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

styles = getSampleStyleSheet()
style_title = ParagraphStyle("EnTitle", parent=styles["Title"], fontSize=18)
style_heading = ParagraphStyle("EnHeading", parent=styles["Heading2"], fontSize=13)
style_body = ParagraphStyle("EnBody", parent=styles["Normal"], fontSize=10, leading=14)
style_table = ParagraphStyle("EnTable", fontSize=9, leading=12)


def _p(text):
    return Paragraph(text, style_table)


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])


def create_drug_guideline_en():
    """Drug Deferral Guidelines PDF (English)"""
    path = os.path.join(DATA_DIR, "guideline_drug_en.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("Blood Donation Screening — Drug Deferral Guidelines", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. OTC Medication Deferral Periods", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "When a prospective donor has taken medication, eligibility is determined based on the type of drug "
        "and purpose of use. The table below summarizes deferral periods for common OTC medications.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data = [
        [_p("Drug"), _p("Active Ingredient"), _p("Eligibility"), _p("Deferral Period"), _p("Reason")],
        [_p("Aspirin"), _p("Acetylsalicylic acid"), _p("Conditional"),
         _p("36 hours after last dose<br/>for whole blood donation"),
         _p("Irreversible platelet inhibition.<br/>Platelet donation requires 3-day wait.")],
        [_p("Tylenol<br/>(Acetaminophen)"), _p("Acetaminophen"), _p("Eligible immediately"),
         _p("No deferral"),
         _p("No effect on platelet function.<br/>Eligible immediately for analgesic use.")],
        [_p("Ibuprofen"), _p("Ibuprofen"), _p("Conditional"),
         _p("24 hours after last dose"),
         _p("Reversible platelet inhibition.<br/>Function recovers after 24 hours.")],
        [_p("Antihistamines<br/>(Cetirizine, etc.)"), _p("Cetirizine / Loratadine"), _p("Eligible immediately"),
         _p("No deferral"),
         _p("For allergy treatment.<br/>No effect on blood components.")],
        [_p("Antibiotics<br/>(Amoxicillin, etc.)"), _p("Amoxicillin / Cephalexin"), _p("Conditional"),
         _p("After completing course<br/>and symptom resolution"),
         _p("Antibiotics for infection require completion<br/>of course and symptom resolution.")],
    ]
    t = Table(data, colWidths=[55*mm, 35*mm, 30*mm, 45*mm, 55*mm])
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. Antihypertensive Medication Guidelines", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "For donors taking antihypertensive medication, blood pressure readings are the key factor. "
        "If blood pressure is stable within the normal range, donation is permitted.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data2 = [
        [_p("Drug Class"), _p("Examples"), _p("Eligibility"), _p("Condition"), _p("Notes")],
        [_p("ACE Inhibitors"), _p("Enalapril, Ramipril"), _p("Conditional"),
         _p("Systolic 90-179 mmHg<br/>Diastolic < 100 mmHg"),
         _p("Eligible if BP within range<br/>and no complications")],
        [_p("ARBs"), _p("Losartan, Valsartan"), _p("Conditional"),
         _p("Systolic 90-179 mmHg<br/>Diastolic < 100 mmHg"),
         _p("Single agent, stable BP")],
        [_p("Beta Blockers"), _p("Atenolol, Metoprolol"), _p("Conditional"),
         _p("Systolic 90-179 mmHg<br/>Diastolic < 100 mmHg"),
         _p("Pulse must be >= 50 bpm")],
        [_p("CCBs"), _p("Amlodipine, Nifedipine"), _p("Conditional"),
         _p("Systolic 90-179 mmHg<br/>Diastolic < 100 mmHg"),
         _p("Confirmed stable BP control")],
    ]
    t2 = Table(data2, colWidths=[35*mm, 40*mm, 30*mm, 45*mm, 55*mm])
    t2.setStyle(_table_style())
    elements.append(t2)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. Permanently Deferred Medications", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "The following medications result in mandatory deferral from blood donation:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data3 = [
        [_p("Drug"), _p("Deferral Period"), _p("Reason")],
        [_p("Isotretinoin (Accutane)"), _p("1 month after discontinuation"),
         _p("Risk of birth defects. May remain in blood.")],
        [_p("Finasteride (Propecia)"), _p("1 month after discontinuation"),
         _p("Risk of birth defects.")],
        [_p("Dutasteride (Avodart)"), _p("6 months after discontinuation"),
         _p("Long half-life, prolonged blood retention.")],
        [_p("Acitretin (Soriatane)"), _p("3 years after discontinuation"),
         _p("Extremely long half-life. Teratogenic.")],
        [_p("Etretinate (Tegison)"), _p("Permanent deferral"),
         _p("May remain in body permanently.")],
    ]
    t3 = Table(data3, colWidths=[55*mm, 50*mm, 80*mm])
    t3.setStyle(_table_style())
    elements.append(t3)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "* Based on Korean Red Cross Blood Donation Record Screening Criteria, 22nd Edition. "
        "Final determination is made by the screening nurse.",
        style_body
    ))

    doc.build(elements)
    print(f"Created: {path}")


def create_malaria_guideline_en():
    """Malaria Risk Region Guidelines PDF (English)"""
    path = os.path.join(DATA_DIR, "guideline_malaria_en.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("Blood Donation Screening — Malaria Risk Regions", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. Deferral Periods by Malaria Risk Region", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "Prospective donors who have visited malaria-risk regions are subject to deferral periods "
        "based on the WHO risk classification of the region visited. Deferral periods apply regardless "
        "of whether symptoms are present.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data = [
        [_p("Region"), _p("Country"), _p("WHO Risk Level"), _p("Deferral Period"), _p("Notes")],
        [_p("Southeast Asia"), _p("Indonesia (Bali)"), _p("Low risk"),
         _p("1 month after return"),
         _p("Bali classified as low risk.<br/>Eligible after 1 month if asymptomatic.")],
        [_p("Southeast Asia"), _p("Indonesia (Papua)"), _p("High risk"),
         _p("1 year after return"),
         _p("Papua is high risk.<br/>1-year deferral, malaria test recommended.")],
        [_p("Southeast Asia"), _p("Thailand (Bangkok)"), _p("Low risk"),
         _p("1 month after return"),
         _p("Bangkok city is low risk.<br/>Northern border areas are moderate risk.")],
        [_p("Southeast Asia"), _p("Vietnam (Hanoi/HCMC)"), _p("Low risk"),
         _p("1 month after return"),
         _p("Major cities are low risk.<br/>Central highlands are moderate risk.")],
        [_p("South Asia"), _p("India (Delhi/Mumbai)"), _p("Moderate risk"),
         _p("6 months after return"),
         _p("Urban areas also moderate risk.<br/>Rural visits classified as high risk.")],
        [_p("Africa"), _p("Kenya"), _p("High risk"),
         _p("1 year after return"),
         _p("All sub-Saharan Africa is high risk.")],
        [_p("Africa"), _p("Nigeria"), _p("High risk"),
         _p("1 year after return"),
         _p("One of the highest malaria incidence countries.")],
        [_p("Africa"), _p("Tanzania"), _p("High risk"),
         _p("1 year after return"),
         _p("High risk throughout, including Zanzibar.")],
        [_p("Latin America"), _p("Brazil (Amazon)"), _p("Moderate risk"),
         _p("6 months after return"),
         _p("Amazon basin is moderate risk.<br/>Cities like Sao Paulo are low risk.")],
        [_p("Latin America"), _p("Mexico"), _p("Low risk"),
         _p("1 month after return"),
         _p("Most tourist areas are low risk.")],
    ]
    t = Table(data, colWidths=[30*mm, 40*mm, 30*mm, 35*mm, 60*mm])
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. Additional Deferral for Malaria Prophylaxis", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "If the donor took malaria prophylaxis (mefloquine, doxycycline, atovaquone-proguanil, etc.), "
        "an additional deferral period of at least 3 months after completing the medication applies, "
        "separate from the regional deferral period.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. History of Malaria Infection", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "Donors with a history of malaria infection are deferred for 3 years after confirmed cure. "
        "If malaria antibody test is positive after 3 years, donation remains ineligible.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("4. Domestic Malaria Risk Areas (South Korea)", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "Northern Gyeonggi Province (Paju, Yeoncheon, Cheorwon) and Northern Gangwon Province "
        "(Cheorwon, Hwacheon, Yanggu) are designated domestic malaria risk areas. Residents or "
        "military personnel in these areas are deferred for 2 years after leaving the area.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "* Based on Korean Red Cross Blood Donation Record Screening Criteria, 22nd Edition, "
        "and WHO World Malaria Report (2024).",
        style_body
    ))

    doc.build(elements)
    print(f"Created: {path}")


def create_main_guideline_en():
    """General Screening Criteria PDF (English)"""
    path = os.path.join(DATA_DIR, "guideline_main_en.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("Blood Donation Screening — General Criteria", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. Basic Eligibility Requirements", style_heading))
    elements.append(Spacer(1, 5*mm))

    data_basic = [
        [_p("Criteria"), _p("Whole Blood (320/400mL)"), _p("Platelet Apheresis"), _p("Plasma Apheresis")],
        [_p("Age"), _p("16-69 years"), _p("17-59 years"), _p("17-69 years")],
        [_p("Weight"), _p("M: >= 50kg / F: >= 45kg"), _p("M: >= 50kg / F: >= 45kg"), _p("M: >= 50kg / F: >= 45kg")],
        [_p("BP (Systolic)"), _p("90-179 mmHg"), _p("90-179 mmHg"), _p("90-179 mmHg")],
        [_p("BP (Diastolic)"), _p("< 100 mmHg"), _p("< 100 mmHg"), _p("< 100 mmHg")],
        [_p("Pulse"), _p("60-100 bpm"), _p("60-100 bpm"), _p("60-100 bpm")],
        [_p("Temperature"), _p("<= 37.5 C"), _p("<= 37.5 C"), _p("<= 37.5 C")],
        [_p("Hemoglobin"), _p("M: >= 13.0 / F: >= 12.5 g/dL"), _p("M: >= 13.0 / F: >= 12.5 g/dL"), _p("M: >= 13.0 / F: >= 12.5 g/dL")],
        [_p("Donation Interval"), _p("8 weeks after whole blood"), _p("2 weeks after apheresis"), _p("2 weeks after apheresis")],
    ]
    t1 = Table(data_basic, colWidths=[40*mm, 50*mm, 45*mm, 45*mm])
    t1.setStyle(_table_style())
    elements.append(t1)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. Blood Pressure Assessment Details", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "If blood pressure measured at the time of donation falls outside the following criteria, "
        "donation is not permitted:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data_bp = [
        [_p("BP Type"), _p("Normal Range"), _p("Eligible"), _p("Ineligible")],
        [_p("Systolic"), _p("90-139 mmHg"), _p("90-179 mmHg"),
         _p(">= 180 mmHg or < 90 mmHg")],
        [_p("Diastolic"), _p("60-89 mmHg"), _p("< 100 mmHg"),
         _p(">= 100 mmHg")],
    ]
    t2 = Table(data_bp, colWidths=[40*mm, 45*mm, 45*mm, 55*mm])
    t2.setStyle(_table_style())
    elements.append(t2)

    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "For borderline BP (systolic 140-179 mmHg), antihypertensive use and complications are assessed. "
        "If treated and BP is stable, donation is permitted. "
        "Systolic >= 180 mmHg is ineligible regardless of treatment.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. Permanent Deferral Criteria", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "The following conditions permanently disqualify a donor:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data_perm = [
        [_p("Reason"), _p("Details")],
        [_p("HIV/AIDS"), _p("Confirmed positive")],
        [_p("Hepatitis B/C carrier"), _p("HBsAg positive or HCV antibody positive")],
        [_p("vCJD risk"), _p("UK residence >= 3 months (1980-1996),<br/>Europe residence >= 5 years (1980-2004)")],
        [_p("IV drug use history"), _p("Any history of intravenous drug use")],
        [_p("Organ/tissue transplant recipient"), _p("Xenogeneic or allogeneic transplant recipient")],
        [_p("Hemophilia/coagulation disorders"), _p("Congenital coagulation factor deficiency")],
    ]
    t3 = Table(data_perm, colWidths=[55*mm, 120*mm])
    t3.setStyle(_table_style())
    elements.append(t3)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("4. Screening Procedure Summary (For Nurses)", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "1) Review electronic questionnaire -> 2) Verify ID and identity -> "
        "3) Measure BP, pulse, temperature -> 4) Hemoglobin test (finger stick) -> "
        "5) In-person screening (travel, drugs, surgery, conditions) -> "
        "6) Final determination and consent form -> 7) Proceed with collection",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "The screening nurse conducts follow-up questions based on the electronic questionnaire. "
        "Cases not covered by the criteria are referred to the medical officer.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("5. Temporary Deferral Criteria (Key Items)", style_heading))
    elements.append(Spacer(1, 5*mm))

    data_temp = [
        [_p("Reason"), _p("Deferral Period"), _p("Notes")],
        [_p("Cold/flu symptoms"), _p("1 week after symptom resolution"),
         _p("Fever, cough, sore throat, etc.")],
        [_p("Dental procedure (extraction)"), _p("72 hours after procedure"),
         _p("Simple scaling: same-day eligible")],
        [_p("Tattoo/piercing"), _p("6 months after procedure"),
         _p("When performed outside medical facility")],
        [_p("Blood transfusion received"), _p("1 year after transfusion"),
         _p("Counted from date of transfusion")],
        [_p("Endoscopy (with biopsy)"), _p("6 months after procedure"),
         _p("Simple endoscopy: 1 week")],
        [_p("Vaccination (live vaccine)"), _p("4 weeks after vaccination"),
         _p("Inactivated vaccine: 24 hours")],
        [_p("Pregnancy/childbirth"), _p("6 months after delivery"),
         _p("Also applies during breastfeeding")],
    ]
    t4 = Table(data_temp, colWidths=[50*mm, 45*mm, 80*mm])
    t4.setStyle(_table_style())
    elements.append(t4)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "* Based on Korean Red Cross Blood Donation Record Screening Criteria, 22nd Edition. "
        "All determinations are made by the screening nurse. Uncertain cases are referred to the medical officer.",
        style_body
    ))

    doc.build(elements)
    print(f"Created: {path}")


if __name__ == "__main__":
    create_drug_guideline_en()
    create_malaria_guideline_en()
    create_main_guideline_en()
    print("\nAll English PDFs created!")
