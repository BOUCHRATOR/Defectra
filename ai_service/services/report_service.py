# ==========================================================
# services/report_service.py
# ==========================================================

import os
from datetime import datetime

from database.models import Report
from database.repository import Repository

from services.qa_service import ask
from services.pdf_service import PDFService


class ReportService:

    # ======================================================
    # INIT
    # ======================================================

    def __init__(self, db):

        self.repository = Repository(db)

    # ======================================================
    # CONSTRUIRE LE PROMPT
    # ======================================================

    def build_prompt(
        self,
        vehicle,
        inspection,
        defects
    ):

        prompt = f"""
You are an automotive inspection expert.

Vehicle information

Brand : {vehicle.brand}
Model : {vehicle.model}
Plate : {vehicle.plate_number}
Year : {vehicle.year}

Inspection

Date : {inspection.inspection_date}

Detected defects
"""

        # --------------------------------------------------
        # AUCUN DEFAUT
        # --------------------------------------------------

        if not defects:

            prompt += """
No defects were detected.
"""

        # --------------------------------------------------
        # DEFAUTS
        # --------------------------------------------------

        else:

            for defect in defects:

                prompt += f"""

Defect : {defect.defect_name}

Confidence :
{round(defect.confidence * 100, 2)} %

Severity :
{defect.severity}

Description :
{defect.description}

Suggested solution :
{defect.solution}

"""

        # --------------------------------------------------
        # INSTRUCTIONS
        # --------------------------------------------------

        prompt += """

Generate a professional vehicle inspection report.

The report must contain:

1. Inspection summary
2. Overall vehicle condition
3. Maintenance recommendations

Answer in English.

Markdown formatting is allowed.
"""

        return prompt

    # ======================================================
    # APPEL LLM
    # ======================================================

    def call_llm(
        self,
        prompt
    ):

        print()
        print("========================================")
        print("APPEL LLM RAPPORT")
        print("========================================")

        start = datetime.now()

        try:

            response = ask(prompt)

        except Exception as e:

            print()
            print(
                "ERREUR LLM :",
                str(e)
            )

            raise

        end = datetime.now()

        print(
            "Temps LLM :",
            end - start
        )

        if response is None:

            return (
                "No AI summary was generated."
            )

        return str(response)

    # ======================================================
    # CONDITION DU VEHICULE
    # ======================================================

    def calculate_condition(
        self,
        defects
    ):

        if not defects:

            return "Excellent"

        severe = 0

        for defect in defects:

            severity = (
                str(
                    defect.severity or ""
                )
                .strip()
                .lower()
            )

            if severity in [
                "critical",
                "high",
                "severe"
            ]:

                severe += 1

        if severe >= 3:

            return "Critical"

        elif severe == 2:

            return "Poor"

        elif severe == 1:

            return "Fair"

        else:

            return "Good"

    # ======================================================
    # RECOMMANDATIONS
    # ======================================================

    def build_recommendation(
        self,
        defects
    ):

        if not defects:

            return (
                "No maintenance is required. "
                "The vehicle is in excellent condition."
            )

        recommendations = []

        for defect in defects:

            # ------------------------------------------------
            # SOLUTION DEJA DISPONIBLE
            # ------------------------------------------------

            if (
                defect.solution
                and defect.solution.strip()
            ):

                solution = defect.solution

            else:

                defect_name = (
                    str(
                        defect.defect_name or ""
                    )
                    .strip()
                    .lower()
                )

                if defect_name == "scratch":

                    solution = (
                        "Sand the damaged area, "
                        "repaint it and apply "
                        "a protective polish."
                    )

                elif defect_name == "dent":

                    solution = (
                        "Repair the dent using "
                        "Paintless Dent Repair "
                        "(PDR) if possible."
                    )

                elif defect_name == "crack":

                    solution = (
                        "Repair or replace the "
                        "cracked part immediately "
                        "to ensure safety."
                    )

                else:

                    solution = (
                        "Consult a certified "
                        "technician for further "
                        "inspection."
                    )

            recommendations.append(
                f"• {defect.defect_name}: {solution}"
            )

        return "\n".join(
            recommendations
        )

    # ======================================================
    # CHERCHER RAPPORT EXISTANT
    # ======================================================

    def get_existing_report(
        self,
        inspection_id
    ):

        print()
        print(
            "Recherche rapport existant..."
        )

        try:

            report = (
                self.repository.db
                .query(Report)
                .filter(
                    Report.inspection_id
                    == inspection_id
                )
                .first()
            )

            if report:

                print(
                    "Rapport existant trouvé :",
                    report.id
                )

            else:

                print(
                    "Aucun rapport existant."
                )

            return report

        except Exception as e:

            print(
                "ERREUR recherche rapport :",
                str(e)
            )

            return None

    # ======================================================
    # VERIFIER PDF EXISTANT
    # ======================================================

    def get_existing_pdf_path(
        self,
        report
    ):

        if not report:

            return None

        if not report.pdf_file:

            return None

        pdf_path = str(
            report.pdf_file
        )

        # --------------------------------------------------
        # NORMALISER CHEMIN
        # --------------------------------------------------

        pdf_path = pdf_path.replace(
            "\\",
            os.sep
        )

        # --------------------------------------------------
        # TEST DIRECT
        # --------------------------------------------------

        if os.path.isfile(
            pdf_path
        ):

            return pdf_path

        # --------------------------------------------------
        # SI LE DB CONTIENT UN CHEMIN RELATIF
        # --------------------------------------------------

        possible_paths = [

            os.path.abspath(
                pdf_path
            ),

            os.path.abspath(
                os.path.join(
                    os.path.dirname(
                        os.path.dirname(
                            __file__
                        )
                    ),
                    pdf_path
                )
            )
        ]

        for path in possible_paths:

            if os.path.isfile(path):

                return path

        return None

    # ======================================================
    # SAUVEGARDER / METTRE A JOUR REPORT
    # ======================================================

    def save_report(
        self,
        inspection_id,
        summary,
        condition,
        recommendation
    ):

        # ==================================================
        # CHERCHER EXISTANT
        # ==================================================

        existing_report = (
            self.get_existing_report(
                inspection_id
            )
        )

        # ==================================================
        # METTRE A JOUR
        # ==================================================

        if existing_report:

            print()
            print(
                "Mise à jour du rapport :",
                existing_report.id
            )

            existing_report.summary = (
                summary
            )

            existing_report.overall_condition = (
                condition
            )

            existing_report.recommendation = (
                recommendation
            )

            existing_report.generated_at = (
                datetime.now()
            )

            self.repository.db.commit()

            self.repository.db.refresh(
                existing_report
            )

            return existing_report

        # ==================================================
        # CREER
        # ==================================================

        print()
        print(
            "Création d'un nouveau rapport..."
        )

        report = Report(

            inspection_id=
                inspection_id,

            summary=
                summary,

            overall_condition=
                condition,

            recommendation=
                recommendation,

            generated_at=
                datetime.now()
        )

        try:

            report = (
                self.repository
                .create_report(report)
            )

        except Exception:

            self.repository.db.rollback()

            # ------------------------------------------------
            # PROTECTION CONTRE RACE CONDITION
            # ------------------------------------------------

            existing_report = (
                self.get_existing_report(
                    inspection_id
                )
            )

            if existing_report:

                return existing_report

            raise

        return report

    # ======================================================
    # REPONSE STANDARD
    # ======================================================

    def build_response(
        self,
        report,
        inspection,
        vehicle
    ):

        return {

            "report_id":
                report.id,

            "inspection_id":
                inspection.id,

            "vehicle": {

                "brand":
                    vehicle.brand,

                "model":
                    vehicle.model,

                "plate":
                    vehicle.plate_number

            },

            "summary":
                report.summary,

            "overall_condition":
                report.overall_condition,

            "recommendation":
                report.recommendation,

            "pdf_file":
                report.pdf_file
        }

    # ======================================================
    # GENERER RAPPORT
    # ======================================================

    def generate_report(
        self,
        inspection_id
    ):

        print()
        print("========================================")
        print("REPORT SERVICE")
        print("========================================")

        print(
            "Inspection ID :",
            inspection_id
        )

        # ==================================================
        # INSPECTION
        # ==================================================

        inspection = (
            self.repository
            .get_inspection(
                inspection_id
            )
        )

        if inspection is None:

            print(
                "Inspection introuvable."
            )

            return {
                "error":
                    "Inspection not found"
            }

        # ==================================================
        # VEHICULE
        # ==================================================

        vehicle = (
            self.repository
            .get_vehicle_by_id(
                inspection.vehicle_id
            )
        )

        if vehicle is None:

            print(
                "Véhicule introuvable."
            )

            return {
                "error":
                    "Vehicle not found"
            }

        # ==================================================
        # RAPPORT EXISTANT
        # ==================================================

        existing_report = (
            self.get_existing_report(
                inspection_id
            )
        )

        # ==================================================
        # PDF EXISTANT
        # ==================================================

        if existing_report:

            existing_pdf = (
                self.get_existing_pdf_path(
                    existing_report
                )
            )

            if existing_pdf:

                print()
                print("========================================")
                print("✅ RAPPORT EXISTANT")
                print("========================================")

                print(
                    "Report ID :",
                    existing_report.id
                )

                print(
                    "PDF :",
                    existing_pdf
                )

                print(
                    "Aucune régénération LLM/PDF."
                )

                print(
                    "========================================"
                )

                return self.build_response(
                    existing_report,
                    inspection,
                    vehicle
                )

        # ==================================================
        # DEFAUTS
        # ==================================================

        defects = (
            self.repository
            .get_defects_by_inspection(
                inspection_id
            )
        )

        print()
        print(
            "Nombre de défauts :",
            len(defects)
        )

        # ==================================================
        # PROMPT
        # ==================================================

        prompt = self.build_prompt(
            vehicle,
            inspection,
            defects
        )

        # ==================================================
        # LLM
        # ==================================================

        print()
        print(
            "Pas de PDF existant."
        )

        print(
            "Génération du résumé LLM..."
        )

        summary = self.call_llm(
            prompt
        )

        # ==================================================
        # CONDITION
        # ==================================================

        condition = (
            self.calculate_condition(
                defects
            )
        )

        print(
            "Condition :",
            condition
        )

        # ==================================================
        # RECOMMANDATION
        # ==================================================

        recommendation = (
            self.build_recommendation(
                defects
            )
        )

        # ==================================================
        # SAVE REPORT
        # ==================================================

        report = self.save_report(
            inspection_id=
                inspection_id,

            summary=
                summary,

            condition=
                condition,

            recommendation=
                recommendation
        )

        print()
        print(
            "Report ID :",
            report.id
        )

        # ==================================================
        # PDF
        # ==================================================

        print()
        print("========================================")
        print("GENERATION PDF")
        print("========================================")

        pdf_service = PDFService()

        start_pdf = datetime.now()

        try:

            pdf_path = (
                pdf_service.generate(
                    report=
                        report,

                    inspection=
                        inspection,

                    vehicle=
                        vehicle,

                    defects=
                        defects
                )
            )

        except Exception as e:

            print()
            print(
                "ERREUR GENERATION PDF :",
                str(e)
            )

            self.repository.db.rollback()

            raise

        end_pdf = datetime.now()

        print(
            "Temps PDF :",
            end_pdf - start_pdf
        )

        # ==================================================
        # VERIFIER PDF
        # ==================================================

        if not pdf_path:

            raise RuntimeError(
                "PDFService n'a retourné "
                "aucun chemin de fichier."
            )

        pdf_path = str(
            pdf_path
        )

        print(
            "PDF path :",
            pdf_path
        )

        if not os.path.isfile(
            pdf_path
        ):

            raise RuntimeError(
                "Le PDF a été annoncé comme "
                "généré mais le fichier "
                "n'existe pas : "
                f"{pdf_path}"
            )

        print(
            "PDF existe :",
            True
        )

        print(
            "PDF taille :",
            os.path.getsize(
                pdf_path
            ),
            "bytes"
        )

        # ==================================================
        # ENREGISTRER PDF
        # ==================================================

        report.pdf_file = pdf_path

        self.repository.db.commit()

        self.repository.db.refresh(
            report
        )

        # ==================================================
        # RESULTAT
        # ==================================================

        result = self.build_response(
            report,
            inspection,
            vehicle
        )

        print()
        print("========================================")
        print("RAPPORT TERMINE")
        print("========================================")

        print(
            "Report ID :",
            report.id
        )

        print(
            "Inspection ID :",
            inspection.id
        )

        print(
            "PDF :",
            report.pdf_file
        )

        print("========================================")

        return result