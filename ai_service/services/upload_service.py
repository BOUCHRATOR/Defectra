import json
from datetime import datetime

from config import MOCK_DATA

from database.models import (
    Inspection,
    Defect
)

from database.repository import Repository


class UploadService:

    def __init__(self, db):

        self.repository = Repository(db)

    # =====================================================
    # Charger les détections mock
    # =====================================================

    def load_detection(self):

        with open(MOCK_DATA, "r", encoding="utf-8") as f:

            return json.load(f)

    # =====================================================
    # Créer une inspection
    # =====================================================

    def create_inspection(
        self,
        vehicle_id,
        notes="Automatic inspection"
    ):

        inspection = Inspection(

            vehicle_id=vehicle_id,

            inspection_date=datetime.now().date(),

            notes=notes,

            status="Completed",

            created_at=datetime.now()

        )

        return self.repository.create_inspection(
            inspection
        )

    # =====================================================
    # Sauvegarder les défauts
    # =====================================================

    def save_defects(
        self,
        inspection_id,
        defects
    ):

        saved = []

        for item in defects:

            defect = Defect(

                inspection_id=inspection_id,

                defect_name=item.get("type"),

                confidence=item.get("confidence"),

                severity=item.get("severity"),

                description=item.get("description", ""),

                solution=item.get("solution", ""),

                defect_image=item.get("image", ""),

                created_at=datetime.now()

            )

            saved.append(

                self.repository.create_defect(
                    defect
                )

            )

        return saved

    # =====================================================
    # Pipeline principal
    # =====================================================

    def process_upload(
        self,
        vehicle_id
    ):

        detections = self.load_detection()

        vehicle_detection = None

        for item in detections:

            if item["vehicle_id"] == vehicle_id:

                vehicle_detection = item

                break

        if vehicle_detection is None:

            raise Exception(
                f"No mock detection found for vehicle_id={vehicle_id}"
            )

        inspection = self.create_inspection(
            vehicle_id
        )

        defects = vehicle_detection["defects"]

        self.save_defects(

            inspection.id,

            defects

        )

        return {

            "inspection_id": inspection.id,

            "vehicle_id": vehicle_id,

            "plate": vehicle_detection["plate"],

            "brand": vehicle_detection["brand"],

            "model": vehicle_detection["model"],

            "year": vehicle_detection["year"],

            "total_defects": len(defects),

            "status": "Inspection completed"

        }