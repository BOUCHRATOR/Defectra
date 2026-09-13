from datetime import date, datetime

from database.models import Inspection, Defect
from database.repository import Repository

from services.inspection_detection_service import (
    InspectionDetectionService
)

from services.qa_service import QAService


# ==========================================================
# INSPECTION SERVICE
# ==========================================================

class InspectionService:

    def __init__(self, db):

        # Session PostgreSQL
        self.db = db

        # Repository
        self.repository = Repository(db)

        # Service YOLO + RT-DETR
        self.detection_service = (
            InspectionDetectionService()
        )

        # Service RAG + LLM
        self.qa_service = QAService(db)

    # ======================================================
    # CREER UNE INSPECTION À PARTIR D'UNE IMAGE
    # ======================================================

    def create_inspection_from_image(
        self,
        image_path,
        vehicle_id
    ):

        # ==================================================
        # 1. RECHERCHER LE VEHICULE
        # ==================================================

        print("\n========================================")
        print("1. RECHERCHE DU VEHICULE")
        print("========================================")

        vehicle = (
            self.repository.get_vehicle_by_id(
                vehicle_id
            )
        )

        if not vehicle:

            raise ValueError(
                f"Véhicule {vehicle_id} introuvable."
            )

        print(
            f"Véhicule trouvé : "
            f"{vehicle.brand} {vehicle.model}"
        )

        print(
            f"Plaque : {vehicle.plate_number}"
        )

        # ==================================================
        # 2. DETECTION YOLO + RT-DETR
        # ==================================================

        print("\n========================================")
        print("2. DETECTION YOLO + RT-DETR")
        print("========================================")

        analysis = (
            self.detection_service.analyze_image(
                image_path
            )
        )

        if not analysis.get("success"):

            raise ValueError(
                analysis.get(
                    "message",
                    "Erreur pendant la détection."
                )
            )

        # ==================================================
        # INFORMATIONS VEHICULE DETECTE
        # ==================================================

        detected_vehicle = analysis.get(
            "vehicle"
        )

        if detected_vehicle:

            print("\nVOITURE DETECTEE")

            print(
                "Type :",
                detected_vehicle.get("type")
            )

            print(
                "Confiance :",
                detected_vehicle.get("confidence")
            )

        # ==================================================
        # 3. CREER L'INSPECTION
        # ==================================================

        print("\n========================================")
        print("3. CREATION DE L'INSPECTION")
        print("========================================")

        inspection = Inspection(

            vehicle_id=vehicle_id,

            inspection_date=date.today(),

            notes=(
                "Inspection automatique "
                "avec YOLO + RT-DETR + RAG + LLM"
            ),

            status="completed",

            created_at=datetime.now()
        )

        inspection = (
            self.repository.create_inspection(
                inspection
            )
        )

        print(
            f"Inspection créée : "
            f"{inspection.id}"
        )

        # ==================================================
        # 4. RECUPERER LES DEFAUTS
        # ==================================================

        defects = analysis.get(
            "defects",
            []
        )

        if not defects:

            print("\n========================================")
            print("AUCUN DEFAUT DETECTE")
            print("========================================")

            return {

                "success": True,

                "inspection_id":
                    inspection.id,

                "vehicle_id":
                    vehicle_id,

                "defects": []
            }

        # ==================================================
        # LISTE DES DEFAUTS ENREGISTRES
        # ==================================================

        saved_defects = []

        # ==================================================
        # 5. TRAITER CHAQUE DEFAUT
        # ==================================================

        for index, defect_data in enumerate(
            defects,
            start=1
        ):

            print("\n========================================")
            print(
                f"DEFAUT {index}"
            )
            print("========================================")

            # ==================================================
            # DONNEES RT-DETR
            # ==================================================

            defect_name = defect_data.get(
                "type"
            )

            confidence = float(
                defect_data.get(
                    "confidence",
                    0
                )
            )

            location = defect_data.get(
                "location",
                "unknown"
            )

            bbox = defect_data.get(
                "bbox"
            )

            # Vérification bbox
            if not bbox:

                print(
                    "ATTENTION : bbox absente."
                )

                bbox = {

                    "x1": 0,
                    "y1": 0,
                    "x2": 0,
                    "y2": 0
                }

            x1 = float(
                bbox.get(
                    "x1",
                    0
                )
            )

            y1 = float(
                bbox.get(
                    "y1",
                    0
                )
            )

            x2 = float(
                bbox.get(
                    "x2",
                    0
                )
            )

            y2 = float(
                bbox.get(
                    "y2",
                    0
                )
            )

            # ==================================================
            # AFFICHAGE
            # ==================================================

            print(
                "Type :",
                defect_name
            )

            print(
                "Confiance RT-DETR :",
                f"{confidence * 100:.2f}%"
            )

            print(
                "Position :",
                location
            )

            print(
                "Bounding box :",
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            )

            # ==================================================
            # 6. CREER LE DEFAUT DANS POSTGRESQL
            # ==================================================

            print(
                "\nCréation du défaut "
                "dans PostgreSQL..."
            )

            defect = Defect(

                inspection_id=inspection.id,

                defect_name=defect_name,

                confidence=confidence,

                # IMPORTANT :
                # La gravité n'est pas encore connue
                severity=None,

                description=None,

                solution=None,

                location=location,

                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,

                defect_image=image_path,

                created_at=datetime.now()
            )

            defect = (
                self.repository.create_defect(
                    defect
                )
            )

            print(
                f"Défaut créé avec ID : "
                f"{defect.id}"
            )

            # ==================================================
            # 7. RAG + LLM
            # ==================================================

            print("\n========================================")
            print("7. ANALYSE RAG + LLM")
            print("========================================")

            question = f"""
Nous réalisons une inspection automobile.

Le modèle RT-DETR a détecté le défaut suivant :

TYPE DU DEFAUT :
{defect_name}

CONFIANCE DE DETECTION :
{confidence * 100:.2f} %

POSITION SUR LE VEHICULE :
{location}

BOUNDING BOX :
x1 = {x1}
y1 = {y1}
x2 = {x2}
y2 = {y2}


OBJECTIF :

Analyser ce défaut automobile en utilisant :

1. Les informations spécifiques de cette
   inspection disponibles dans PostgreSQL.

2. Les connaissances techniques automobiles
   disponibles dans ChromaDB.


IMPORTANT :

La confiance RT-DETR représente uniquement
la confiance du modèle dans la détection.

Elle ne représente PAS la gravité.

Par exemple :

82% de confiance ne signifie PAS
que le défaut est de gravité HIGH.


Détermine :

1. La gravité :

LOW
MEDIUM
HIGH
ou UNKNOWN


2. Une description technique du défaut.


3. Une solution ou recommandation.


Si les informations disponibles ne permettent
pas de déterminer correctement la gravité,
utilise :

SEVERITY: UNKNOWN


Réponds exactement avec ce format :

SEVERITY: LOW/MEDIUM/HIGH/UNKNOWN

DESCRIPTION:
description technique du défaut

SOLUTION:
solution ou recommandation
"""

            try:

                ai_result = self.qa_service.ask(

                    question=question,

                    inspection_id=inspection.id
                )

            except Exception as e:

                print(
                    "\nERREUR RAG + LLM :",
                    str(e)
                )

                ai_result = ""

            # ==================================================
            # AFFICHER REPONSE LLM
            # ==================================================

            print("\n========================================")
            print("REPONSE DU LLM")
            print("========================================")

            print(
                ai_result
            )

            # ==================================================
            # 8. EXTRAIRE SEVERITY
            # ==================================================

            severity = extract_value(
                ai_result,
                "SEVERITY:"
            )

            # ==================================================
            # 9. EXTRAIRE DESCRIPTION
            # ==================================================

            description = extract_section(

                ai_result,

                "DESCRIPTION:",

                "SOLUTION:"
            )

            # ==================================================
            # 10. EXTRAIRE SOLUTION
            # ==================================================

            solution = extract_section(

                ai_result,

                "SOLUTION:"
            )

            # ==================================================
            # NETTOYER
            # ==================================================

            if severity:

                severity = (
                    severity
                    .strip()
                    .upper()
                )

            else:

                severity = "UNKNOWN"

            if not description:

                description = (
                    "Aucune description "
                    "fournie par le modèle."
                )

            if not solution:

                solution = (
                    "Aucune solution "
                    "fournie par le modèle."
                )

            # ==================================================
            # 11. UPDATE POSTGRESQL
            # ==================================================

            print("\n========================================")
            print("MISE A JOUR POSTGRESQL")
            print("========================================")

            defect.severity = severity

            defect.description = description

            defect.solution = solution

            defect = (
                self.repository.update_defect(
                    defect
                )
            )

            # ==================================================
            # AFFICHER RESULTAT
            # ==================================================

            print(
                "ID :",
                defect.id
            )

            print(
                "Type :",
                defect.defect_name
            )

            print(
                "Confiance :",
                f"{defect.confidence * 100:.2f}%"
            )

            print(
                "Position :",
                defect.location
            )

            print(
                "Gravité :",
                defect.severity
            )

            print(
                "Description :",
                defect.description
            )

            print(
                "Solution :",
                defect.solution
            )

            # ==================================================
            # AJOUTER A LA LISTE
            # ==================================================

            saved_defects.append(
                defect
            )

        # ==================================================
        # 12. RESULTAT FINAL
        # ==================================================

        print("\n========================================")
        print("INSPECTION TERMINEE")
        print("========================================")

        return {

            "success": True,

            "inspection_id":
                inspection.id,

            "vehicle_id":
                vehicle_id,

            "vehicle": {

                "type":
                    detected_vehicle.get(
                        "type"
                    )
                    if detected_vehicle
                    else None,

                "confidence":
                    detected_vehicle.get(
                        "confidence"
                    )
                    if detected_vehicle
                    else None
            },

            "defects": [

                {

                    "id":
                        defect.id,

                    "type":
                        defect.defect_name,

                    "confidence":
                        defect.confidence,

                    "location":
                        defect.location,

                    "bbox": {

                        "x1":
                            defect.x1,

                        "y1":
                            defect.y1,

                        "x2":
                            defect.x2,

                        "y2":
                            defect.y2
                    },

                    "severity":
                        defect.severity,

                    "description":
                        defect.description,

                    "solution":
                        defect.solution
                }

                for defect in saved_defects
            ]
        }


# ==========================================================
# FONCTION : EXTRAIRE UNE VALEUR
# ==========================================================

def extract_value(
    text,
    key
):

    if not text:

        return None

    for line in text.splitlines():

        line = line.strip()

        if line.upper().startswith(
            key.upper()
        ):

            parts = line.split(
                ":",
                1
            )

            if len(parts) == 2:

                return parts[1].strip()

    return None


# ==========================================================
# FONCTION : EXTRAIRE UNE SECTION
# ==========================================================

def extract_section(
    text,
    start_key,
    end_key=None
):

    if not text:

        return None

    text_upper = text.upper()

    start = text_upper.find(
        start_key.upper()
    )

    if start == -1:

        return None

    start = start + len(
        start_key
    )

    # ------------------------------------------------------
    # Si une clé de fin existe
    # ------------------------------------------------------

    if end_key:

        end = text_upper.find(
            end_key.upper(),
            start
        )

        if end == -1:

            end = len(text)

    else:

        end = len(text)

    return text[start:end].strip()