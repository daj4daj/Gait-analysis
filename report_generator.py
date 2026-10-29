"""
Clinical Physical Therapy Gait Assessment Report Generator
Generates comprehensive, publication-quality biomechanical assessment PDF reports
for Physical Therapists, Physicians, and Rehabilitation Teams using ReportLab.
"""

import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds professional header, footer, page count, and confidentiality watermark."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "PHYSICAL THERAPY BIOMECHANICAL GAIT ASSESSMENT")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 26, "CONFIDENTIAL MEDICAL RECORD")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 36, 8.5 * inch - 36, 36)

        footer_text = "CONFIDENTIAL CLINICAL RECORD - For Physical Therapy & Medical Rehabilitation Use Only"
        self.drawString(36, 24, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 24, page_str)
        self.restoreState()


class GaitReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        # Healthcare color palette
        self.c_primary = colors.HexColor("#0F172A")    # Deep slate
        self.c_brand = colors.HexColor("#0D9488")      # Teal medical
        self.c_accent = colors.HexColor("#2563EB")     # Blue
        self.c_gray_bg = colors.HexColor("#F8FAFC")
        self.c_border = colors.HexColor("#E2E8F0")

        self.style_title = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=self.c_primary
        )

        self.style_subtitle = ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )

        self.style_section_h1 = ParagraphStyle(
            'SectionH1',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=self.c_brand,
            spaceBefore=10,
            spaceAfter=4
        )

        self.style_body = ParagraphStyle(
            'BodyClean',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=self.c_primary
        )

        self.style_body_bold = ParagraphStyle(
            'BodyCleanBold',
            parent=self.style_body,
            fontName='Helvetica-Bold'
        )

        self.style_table_cell = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=self.c_primary
        )

        self.style_table_header = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=colors.white
        )

    def generate_pdf(self, gait_data, chart_paths, patient_info, output_pdf_path):
        """
        Builds the complete multi-page Physical Therapy Gait Evaluation PDF.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=46
        )

        story = []

        # 1. Header & Clinic Banner
        story.extend(self._build_header_section())

        # 2. Patient Demographics & Evaluation Metadata
        story.extend(self._build_patient_meta_table(patient_info, gait_data))
        story.append(Spacer(1, 8))

        # 3. Executive Scorecard / Key Mobility Metrics
        story.extend(self._build_executive_scorecard(gait_data))
        story.append(Spacer(1, 10))

        # 4. Spatiotemporal & Kinematic Parameter Table
        story.extend(self._build_kinematics_table(gait_data))
        story.append(Spacer(1, 12))

        # 5. Kinematic Graphs (Knee, Hip, Gait Phase Distribution)
        story.extend(self._build_charts_section(chart_paths))
        story.append(Spacer(1, 10))

        # 6. Observational Gait Deviations & Pathologies
        story.extend(self._build_deviations_section(gait_data))
        story.append(Spacer(1, 10))

        # 7. Targeted Physical Therapy Rehabilitation Prescription
        story.extend(self._build_pt_plan_section(gait_data))
        story.append(Spacer(1, 10))

        # 8. Physical Therapist Notes & Signature Section
        story.extend(self._build_signoff_section(patient_info))

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_pdf_path

    def _build_header_section(self):
        story = []
        header_table_data = [
            [
                Paragraph("<b>ADVANCED REHABILITATION & BIOMECHANICS CLINIC</b><br/>"
                          "<font size=8 color='#64748B'>Department of Physical Therapy & Clinical Motion Analysis</font>", self.style_body),
                Paragraph("<font size=8 color='#64748B'><b>Lab Location:</b> Main Clinic - Motion Lab 2<br/>"
                          f"<b>Assessment Date:</b> {datetime.datetime.now().strftime('%B %d, %Y')}</font>", self.style_body)
            ]
        ]
        t = Table(header_table_data, colWidths=[4.2 * inch, 3.2 * inch])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=2, color=self.c_brand, spaceAfter=8))
        story.append(Paragraph("PHYSICAL THERAPY BIOMECHANICAL GAIT ASSESSMENT", self.style_title))
        story.append(Paragraph("Objective Kinematic, Spatiotemporal & Dynamic Gait Analysis with Evidence-Based Rehabilitation Protocol", self.style_subtitle))
        story.append(Spacer(1, 8))
        return story

    def _build_patient_meta_table(self, info, gait_data):
        story = []
        name = info.get("name", "Jane Doe")
        mrn = info.get("mrn", "MRN-849201")
        age = str(info.get("age", "42"))
        gender = info.get("gender", "Female")
        physician = info.get("physician", "Dr. Robert Vance, MD (Orthopedics)")
        therapist = info.get("therapist", "Dr. Sarah Mitchell, PT, DPT, OCS")
        complaint = info.get("complaint", "Difficulty with prolonged ambulation, right knee giving way / hyperextension during stance, persistent fatigue.")

        meta_data = [
            [
                Paragraph(f"<b>Patient Name:</b> {name}", self.style_table_cell),
                Paragraph(f"<b>MRN / ID:</b> {mrn}", self.style_table_cell),
                Paragraph(f"<b>Age / Sex:</b> {age} yrs / {gender}", self.style_table_cell)
            ],
            [
                Paragraph(f"<b>Referring MD:</b> {physician}", self.style_table_cell),
                Paragraph(f"<b>Evaluating PT:</b> {therapist}", self.style_table_cell),
                Paragraph(f"<b>Evaluation Duration:</b> {gait_data.get('duration_sec', 5.0)}s ({gait_data.get('total_frames', 150)} frames)", self.style_table_cell)
            ],
            [
                Paragraph(f"<b>Chief Complaint / Clinical Indication:</b> {complaint}", self.style_table_cell),
                "", ""
            ]
        ]
        t = Table(meta_data, colWidths=[2.6 * inch, 2.5 * inch, 2.3 * inch])
        t.setStyle(TableStyle([
            ('SPAN', (0, 2), (2, 2)),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 1, self.c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.c_border),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        return story

    def _build_executive_scorecard(self, gait_data):
        story = []
        symmetry = gait_data.get("gait_symmetry_score", 95.0)
        cadence = gait_data.get("cadence", 110.0)
        stride_time = gait_data.get("avg_stride_time", 1.10)
        l_stance = gait_data.get("l_stance_pct", 60.0)
        r_stance = gait_data.get("r_stance_pct", 60.0)

        # Symmetry category
        if symmetry >= 90:
            symm_status = "<font color='#16A34A'><b>HIGH SYMMETRY</b></font>"
            symm_bg = colors.HexColor("#DCFCE7")
        elif symmetry >= 80:
            symm_status = "<font color='#D97706'><b>MILD ASYMMETRY</b></font>"
            symm_bg = colors.HexColor("#FEF3C7")
        else:
            symm_status = "<font color='#DC2626'><b>MARKED ASYMMETRY</b></font>"
            symm_bg = colors.HexColor("#FEE2E2")

        scorecard_data = [
            [
                Paragraph("<font size=7 color='#475569'><b>GAIT SYMMETRY INDEX</b></font><br/>"
                          f"<font size=16 color='#0F172A'><b>{symmetry:.1f}%</b></font><br/>"
                          f"{symm_status}", self.style_body),
                Paragraph("<font size=7 color='#475569'><b>CADENCE</b></font><br/>"
                          f"<font size=16 color='#0F172A'><b>{cadence:.0f}</b></font> <font size=9>steps/min</font><br/>"
                          "<font size=8 color='#16A34A'>Normal: 100-120</font>", self.style_body),
                Paragraph("<font size=7 color='#475569'><b>STRIDE DURATION</b></font><br/>"
                          f"<font size=16 color='#0F172A'><b>{stride_time:.2f}</b></font> <font size=9>sec</font><br/>"
                          "<font size=8 color='#16A34A'>Normal: 1.0 - 1.25s</font>", self.style_body),
                Paragraph("<font size=7 color='#475569'><b>STANCE BALANCE (L/R)</b></font><br/>"
                          f"<font size=13 color='#0F172A'><b>{l_stance:.1f}% / {r_stance:.1f}%</b></font><br/>"
                          "<font size=8 color='#475569'>Normal Stance: 60%</font>", self.style_body),
            ]
        ]
        t = Table(scorecard_data, colWidths=[1.85 * inch, 1.85 * inch, 1.85 * inch, 1.85 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), symm_bg),
            ('BACKGROUND', (1,0), (3,0), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, self.c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.c_border),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        return story

    def _build_kinematics_table(self, data):
        story = []
        story.append(Paragraph("1. SPATIOTEMPORAL & JOINT KINEMATIC METRICS", self.style_section_h1))

        # Helper to flag status
        def get_status(val, norm_min, norm_max, invert=False):
            if val is None:
                return "<font color='#64748B'>N/A</font>"
            if invert:
                if val <= norm_max:
                    return "<font color='#16A34A'><b>Normal</b></font>"
                elif val <= norm_max + 3.0:
                    return "<font color='#D97706'><b>Mild Elev</b></font>"
                else:
                    return "<font color='#DC2626'><b>High</b></font>"
            if norm_min <= val <= norm_max:
                return "<font color='#16A34A'><b>Normal</b></font>"
            elif (norm_min - 4.0) <= val < norm_min or norm_max < val <= (norm_max + 4.0):
                return "<font color='#D97706'><b>Borderline</b></font>"
            else:
                return "<font color='#DC2626'><b>Abnormal</b></font>"

        l_knee_hyp = "<font color='#DC2626'><b>Recurvatum</b></font>" if data["l_knee_min_ext"] < -3.0 else "<font color='#16A34A'><b>Normal</b></font>"
        r_knee_hyp = "<font color='#DC2626'><b>Recurvatum</b></font>" if data["r_knee_min_ext"] < -3.0 else "<font color='#16A34A'><b>Normal</b></font>"

        rows = [
            [
                Paragraph("<b>Biomechanical Parameter</b>", self.style_table_header),
                Paragraph("<b>Left Limb</b>", self.style_table_header),
                Paragraph("<b>Right Limb</b>", self.style_table_header),
                Paragraph("<b>Reference Range</b>", self.style_table_header),
                Paragraph("<b>Unit</b>", self.style_table_header),
                Paragraph("<b>Clinical Status</b>", self.style_table_header),
            ],
            [
                Paragraph("Cadence", self.style_table_cell),
                Paragraph(f"{data['cadence']:.1f}", self.style_table_cell),
                Paragraph(f"{data['cadence']:.1f}", self.style_table_cell),
                Paragraph("100.0 - 120.0", self.style_table_cell),
                Paragraph("steps/min", self.style_table_cell),
                Paragraph(get_status(data['cadence'], 100.0, 120.0), self.style_table_cell)
            ],
            [
                Paragraph("Stride Time Duration", self.style_table_cell),
                Paragraph(f"{data['l_stride_time']:.2f}", self.style_table_cell),
                Paragraph(f"{data['r_stride_time']:.2f}", self.style_table_cell),
                Paragraph("1.00 - 1.25", self.style_table_cell),
                Paragraph("sec", self.style_table_cell),
                Paragraph(get_status(data['avg_stride_time'], 1.0, 1.25), self.style_table_cell)
            ],
            [
                Paragraph("Stance Phase Ratio", self.style_table_cell),
                Paragraph(f"{data['l_stance_pct']:.1f}%", self.style_table_cell),
                Paragraph(f"{data['r_stance_pct']:.1f}%", self.style_table_cell),
                Paragraph("58.0 - 62.0%", self.style_table_cell),
                Paragraph("% cycle", self.style_table_cell),
                Paragraph(get_status(data['l_stance_pct'], 58.0, 62.0), self.style_table_cell)
            ],
            [
                Paragraph("Swing Phase Ratio", self.style_table_cell),
                Paragraph(f"{data['l_swing_pct']:.1f}%", self.style_table_cell),
                Paragraph(f"{data['r_swing_pct']:.1f}%", self.style_table_cell),
                Paragraph("38.0 - 42.0%", self.style_table_cell),
                Paragraph("% cycle", self.style_table_cell),
                Paragraph(get_status(data['l_swing_pct'], 38.0, 42.0), self.style_table_cell)
            ],
            [
                Paragraph("Peak Swing Knee Flexion", self.style_table_cell),
                Paragraph(f"{data['l_knee_max_flex']:.1f}°", self.style_table_cell),
                Paragraph(f"{data['r_knee_max_flex']:.1f}°", self.style_table_cell),
                Paragraph("60.0 - 68.0°", self.style_table_cell),
                Paragraph("degrees", self.style_table_cell),
                Paragraph(f"L: {get_status(data['l_knee_max_flex'], 55.0, 72.0)}<br/>R: {get_status(data['r_knee_max_flex'], 55.0, 72.0)}", self.style_table_cell)
            ],
            [
                Paragraph("Knee Extension in Stance", self.style_table_cell),
                Paragraph(f"{data['l_knee_min_ext']:.1f}°", self.style_table_cell),
                Paragraph(f"{data['r_knee_min_ext']:.1f}°", self.style_table_cell),
                Paragraph("0.0 - 5.0° (neutral)", self.style_table_cell),
                Paragraph("degrees", self.style_table_cell),
                Paragraph(f"L: {l_knee_hyp}<br/>R: {r_knee_hyp}", self.style_table_cell)
            ],
            [
                Paragraph("Max Hip Flexion (Initial Contact)", self.style_table_cell),
                Paragraph(f"{data['l_hip_max_flex']:.1f}°", self.style_table_cell),
                Paragraph(f"{data['r_hip_max_flex']:.1f}°", self.style_table_cell),
                Paragraph("25.0 - 32.0°", self.style_table_cell),
                Paragraph("degrees", self.style_table_cell),
                Paragraph(get_status(data['l_hip_max_flex'], 22.0, 35.0), self.style_table_cell)
            ],
            [
                Paragraph("Forward Trunk Lean", self.style_table_cell),
                Paragraph(f"{data['mean_trunk_lean']:.1f}°", self.style_table_cell),
                Paragraph(f"{data['mean_trunk_lean']:.1f}°", self.style_table_cell),
                Paragraph("1.0 - 5.0°", self.style_table_cell),
                Paragraph("degrees", self.style_table_cell),
                Paragraph(get_status(data['mean_trunk_lean'], 0.0, 6.0, invert=True), self.style_table_cell)
            ],
            [
                Paragraph("Pelvic Obliquity / Drop", self.style_table_cell),
                Paragraph(f"{data['max_pelvic_drop']:.1f}°", self.style_table_cell),
                Paragraph(f"{data['max_pelvic_drop']:.1f}°", self.style_table_cell),
                Paragraph("< 4.0°", self.style_table_cell),
                Paragraph("degrees", self.style_table_cell),
                Paragraph(get_status(data['max_pelvic_drop'], 0.0, 4.0, invert=True), self.style_table_cell)
            ]
        ]

        t = Table(rows, colWidths=[2.2 * inch, 1.0 * inch, 1.0 * inch, 1.4 * inch, 0.7 * inch, 1.1 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.c_brand),
            ('BOX', (0,0), (-1,-1), 1, self.c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        return story

    def _build_charts_section(self, chart_paths):
        story = []
        story.append(KeepTogether([
            Paragraph("2. KINEMATIC TRAJECTORY COMPARISON (0 - 100% GAIT CYCLE)", self.style_section_h1),
            Paragraph("<font size=8 color='#64748B'>Continuous joint motion curves compared against 2-SD normative adult reference corridors (Perry & Burnfield). Shaded band represents healthy normal limits.</font>", self.style_body),
            Spacer(1, 4)
        ]))

        knee_img = chart_paths.get("knee_chart")
        hip_img = chart_paths.get("hip_chart")
        phase_img = chart_paths.get("phase_chart")

        chart_elements = []
        if knee_img and os.path.exists(knee_img):
            chart_elements.append([Image(knee_img, width=7.4 * inch, height=3.2 * inch)])
        if hip_img and os.path.exists(hip_img):
            chart_elements.append([Spacer(1, 4)])
            chart_elements.append([Image(hip_img, width=7.4 * inch, height=3.0 * inch)])
        if phase_img and os.path.exists(phase_img):
            chart_elements.append([Spacer(1, 4)])
            chart_elements.append([Image(phase_img, width=6.2 * inch, height=2.3 * inch)])

        t = Table(chart_elements, colWidths=[7.4 * inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t)
        return story

    def _build_deviations_section(self, gait_data):
        story = []
        story.append(KeepTogether([
            Paragraph("3. CLINICAL GAIT DEVIATIONS & BIOMECHANICAL FINDINGS", self.style_section_h1),
            Paragraph("<font size=8 color='#64748B'>Summary of detected pathological movement strategies, joint compensations, and functional deficits.</font>", self.style_body),
            Spacer(1, 4)
        ]))

        deviations = gait_data.get("deviations", [])
        if not deviations:
            deviations = [{"name": "Normal Symmetric Gait", "side": "Bilateral", "severity": "None", "measured": "Normal", "normal": "Normal", "clinical_impact": "No significant deviations observed."}]

        table_rows = [
            [
                Paragraph("<b>Observed Deviation</b>", self.style_table_header),
                Paragraph("<b>Involved Side</b>", self.style_table_header),
                Paragraph("<b>Severity</b>", self.style_table_header),
                Paragraph("<b>Measured vs Normal</b>", self.style_table_header),
                Paragraph("<b>Biomechanical Impact & Joint Stress</b>", self.style_table_header),
            ]
        ]

        for d in deviations:
            sev = d.get("severity", "Mild")
            if sev in ("Moderate", "Severe"):
                sev_color = "#DC2626"
            elif sev == "Mild":
                sev_color = "#D97706"
            else:
                sev_color = "#16A34A"

            table_rows.append([
                Paragraph(f"<b>{d.get('name', 'Deviation')}</b>", self.style_table_cell),
                Paragraph(d.get("side", "N/A"), self.style_table_cell),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", self.style_table_cell),
                Paragraph(f"{d.get('measured', '')} (Ref: {d.get('normal', '')})", self.style_table_cell),
                Paragraph(d.get("clinical_impact", ""), self.style_table_cell),
            ])

        t = Table(table_rows, colWidths=[2.1 * inch, 0.9 * inch, 0.8 * inch, 1.4 * inch, 2.2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.c_brand),
            ('BOX', (0,0), (-1,-1), 1, self.c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        return story

    def _build_pt_plan_section(self, gait_data):
        story = []
        story.append(KeepTogether([
            Paragraph("4. PHYSICAL THERAPY REHABILITATION PRESCRIPTION", self.style_section_h1),
            Paragraph("<font size=8 color='#64748B'>Tailored, evidence-based therapeutic exercises and neuromotor gait retraining mapped directly to the patient's biomechanical presentation.</font>", self.style_body),
            Spacer(1, 4)
        ]))

        pt_plan = gait_data.get("pt_plan", {})
        exercises = pt_plan.get("exercises", [])
        drills = pt_plan.get("gait_drills", [])
        cues = pt_plan.get("cues", [])
        dosage = pt_plan.get("dosage", "Recommended: 2-3 PT sessions/week for 6 weeks plus daily Home Exercise Program.")

        ex_table_data = [
            [
                Paragraph("<b>Therapeutic Exercise</b>", self.style_table_header),
                Paragraph("<b>Target Musculature & Goal</b>", self.style_table_header),
                Paragraph("<b>Dosage & Prescription</b>", self.style_table_header),
                Paragraph("<b>Clinical Rationale</b>", self.style_table_header),
            ]
        ]

        for ex in exercises:
            ex_table_data.append([
                Paragraph(f"<b>{ex.get('title', '')}</b>", self.style_table_cell),
                Paragraph(ex.get("target", ""), self.style_table_cell),
                Paragraph(ex.get("prescription", ""), self.style_table_cell),
                Paragraph(ex.get("rationale", ""), self.style_table_cell),
            ])

        t_ex = Table(ex_table_data, colWidths=[2.2 * inch, 1.8 * inch, 1.8 * inch, 1.6 * inch])
        t_ex.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.c_accent),
            ('BOX', (0,0), (-1,-1), 1, self.c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_ex)
        story.append(Spacer(1, 6))

        # Drills, Cues & Plan
        cues_text = "<br/>".join([f"• <b>Auditory / Visual Cue:</b> {c}" for c in cues]) if cues else "• Maintain symmetrical cadence and upright posture."
        drills_text = "<br/>".join([f"• <b>Gait Retraining Drill:</b> {d}" for d in drills]) if drills else "• Overground walking with biofeedback."

        combined_info = [
            [
                Paragraph(f"<b>Neuromuscular Gait Retraining & Verbal Cues:</b><br/>{drills_text}<br/>{cues_text}<br/><br/>"
                          f"<b>Prescribed Frequency & Plan of Care:</b> {dosage}", self.style_table_cell)
            ]
        ]
        t_cues = Table(combined_info, colWidths=[7.4 * inch])
        t_cues.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_cues)
        return story

    def _build_signoff_section(self, info):
        story = []
        therapist = info.get("therapist", "Dr. Sarah Mitchell, PT, DPT, OCS")
        license_num = info.get("license", "PT License # 049281-NY")
        today_str = datetime.datetime.now().strftime("%B %d, %Y")

        story.append(KeepTogether([
            Spacer(1, 8),
            Paragraph("5. PHYSICAL THERAPIST CLINICAL SIGN-OFF", self.style_section_h1),
            Spacer(1, 4),
            Table([
                [
                    Paragraph("<b>Physical Therapist Clinical Impressions & Progress Notes:</b><br/>"
                              "Patient demonstrates good cognitive understanding of gait cues. Recommended to begin Phase 1 "
                              "neuromuscular re-education and eccentric quad loading immediately. Re-evaluation of joint kinematics "
                              "scheduled in 4 weeks to quantify improvement in gait symmetry and reduction in hyperextension.", self.style_table_cell),
                    Paragraph(f"<br/><br/><b>Signature:</b> ___________________________<br/>"
                              f"<b>{therapist}</b><br/>"
                              f"{license_num}<br/>"
                              f"<b>Signed Date:</b> {today_str}", self.style_table_cell)
                ]
            ], colWidths=[4.6 * inch, 2.8 * inch],
            style=[
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('BOX', (0,0), (-1,-1), 1, self.c_border),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ])
        ]))
        return story
