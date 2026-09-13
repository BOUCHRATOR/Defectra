from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from config import REPORT_FOLDER


class PDFService:

    def __init__(self):

        REPORT_FOLDER.mkdir(exist_ok=True)

    def generate(
        self,
        report,
        inspection,
        vehicle,
        defects
    ):

        pdf_name = f"inspection_{inspection.id}.pdf"

        pdf_path = REPORT_FOLDER / pdf_name

        doc = SimpleDocTemplate(str(pdf_path))

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        elements = []

        # ===================================================
        # TITLE
        # ===================================================

        elements.append(
            Paragraph(
                "DEFECTRA VEHICLE INSPECTION REPORT",
                title_style
            )
        )

        elements.append(Spacer(1,20))

        # ===================================================
        # VEHICLE
        # ===================================================

        elements.append(
            Paragraph(
                "<b>Vehicle Information</b>",
                styles["Heading2"]
            )
        )

        vehicle_table = Table([

            ["Brand", vehicle.brand],

            ["Model", vehicle.model],

            ["Plate", vehicle.plate_number],

            ["Year", str(vehicle.year)],

            ["Inspection Date", str(inspection.inspection_date)]

        ])

        vehicle_table.setStyle(

            TableStyle([

                ("GRID",(0,0),(-1,-1),1,colors.black),

                ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

                ("BOTTOMPADDING",(0,0),(-1,-1),8)

            ])

        )

        elements.append(vehicle_table)

        elements.append(Spacer(1,20))

        # ===================================================
        # DEFECTS
        # ===================================================

        elements.append(

            Paragraph(
                "<b>Detected Defects</b>",
                styles["Heading2"]
            )

        )

        data = [

            [

                "Defect",

                "Confidence",

                "Severity"

            ]

        ]

        for defect in defects:

            data.append([

                defect.defect_name,

                f"{round(defect.confidence*100,2)} %",

                defect.severity

            ])

        defect_table = Table(data)

        defect_table.setStyle(

            TableStyle([

                ("GRID",(0,0),(-1,-1),1,colors.black),

                ("BACKGROUND",(0,0),(-1,0),colors.grey),

                ("TEXTCOLOR",(0,0),(-1,0),colors.white),

                ("BACKGROUND",(0,1),(-1,-1),colors.beige),

                ("BOTTOMPADDING",(0,0),(-1,-1),8)

            ])

        )

        elements.append(defect_table)

        elements.append(Spacer(1,20))

        # ===================================================
        # SUMMARY
        # ===================================================

        elements.append(

            Paragraph(
                "<b>Inspection Summary</b>",
                styles["Heading2"]
            )

        )

        elements.append(

            Paragraph(
                report.summary.replace("\n","<br/>"),
                styles["BodyText"]
            )

        )

        elements.append(Spacer(1,20))

        # ===================================================
        # CONDITION
        # ===================================================

        elements.append(

            Paragraph(
                "<b>Overall Condition</b>",
                styles["Heading2"]
            )

        )

        elements.append(

            Paragraph(
                report.overall_condition,
                styles["BodyText"]
            )

        )

        elements.append(Spacer(1,20))

        # ===================================================
        # RECOMMENDATION
        # ===================================================

        elements.append(

            Paragraph(
                "<b>Maintenance Recommendation</b>",
                styles["Heading2"]
            )

        )

        elements.append(

            Paragraph(
                report.recommendation.replace("\n","<br/>"),
                styles["BodyText"]
            )

        )

        elements.append(Spacer(1,20))

        # ===================================================
        # FOOTER
        # ===================================================

        elements.append(

            Paragraph(

                f"Generated automatically by DEFECTRA AI<br/>"

                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",

                styles["Italic"]

            )

        )

        doc.build(elements)

        return str(pdf_path)