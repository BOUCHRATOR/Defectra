from ai_service.services.detection_service import DetectionService
from ai_service.services.vehicle_detection_service import VehicleDetectionService
from ai_service.services.location_service import LocationService


class InspectionDetectionService:

    def __init__(self):

        print("Initialisation des modèles...")

        self.defect_detector = DetectionService()

        self.vehicle_detector = VehicleDetectionService()

        self.location_service = LocationService()

        print("Tous les services sont prêts.")

    def analyze_image(self, image_path):

        # ==========================================
        # 1. Détecter la voiture avec YOLO
        # ==========================================

        vehicles = self.vehicle_detector.detect_vehicle(
            image_path
        )

        if not vehicles:

            return {
                "success": False,
                "message": "Aucune voiture détectée."
            }

        # Pour commencer, on prend la voiture
        # ayant la meilleure confiance.

        vehicle = max(
            vehicles,
            key=lambda x: x["confidence"]
        )

        vehicle_bbox = vehicle["bbox"]

        # ==========================================
        # 2. Détecter les défauts avec RT-DETR
        # ==========================================

        defects = self.defect_detector.detect_image(
            image_path
        )

        results = []

        # ==========================================
        # 3. Déterminer la position
        # ==========================================

        for defect in defects:

            defect_center_x = defect["center"]["x"]

            location = self.location_service.get_location(
                defect_center_x,
                vehicle_bbox["x1"],
                vehicle_bbox["x2"]
            )

            results.append({

                "type": defect["type"],

                "confidence": defect["confidence"],

                "bbox": defect["bbox"],

                "center": defect["center"],

                "location": location

            })

        # ==========================================
        # 4. Résultat final
        # ==========================================

        return {

            "success": True,

            "vehicle": {

                "type": vehicle["type"],

                "confidence": vehicle["confidence"],

                "bbox": vehicle_bbox

            },

            "defects": results

        }