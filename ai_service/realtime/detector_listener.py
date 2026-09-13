import json
from pathlib import Path
from datetime import datetime
from utils.mapper import json_to_vehicle
from database.postgres import SessionLocal
from database.repository import Repository
from database.models import Vehicle, Inspection, Defect
# Chemin du fichier JSON simulant RT-DETR
JSON_FILE = Path("mock_data/detections.json")


def receive_detections():
    """
    Lit les détections simulées provenant du fichier JSON
    et les transforme en objets VehicleDetection.
    """

    if not JSON_FILE.exists():
        print("❌ Fichier detections.json introuvable.")
        return []

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    detections = []

    for item in data:
        detections.append(
            json_to_vehicle(item)
        )

    print(f"\n✅ {len(detections)} véhicule(s) reçu(s)\n")

    return detections


def process_detection(vehicle):
    """
    Traite une détection.
    Plus tard cette fonction enregistrera les données dans PostgreSQL.
    """

    print("=" * 60)

    print(f"Véhicule : {vehicle.brand} {vehicle.model}")
    print(f"Plaque   : {vehicle.plate}")
    print(f"Année    : {vehicle.year}")
    print(f"Date     : {vehicle.inspection_date}")

    print("\nDéfauts détectés :")

    for defect in vehicle.defects:

        print(
            f" - {defect.type} | "
            f"Confiance : {defect.confidence:.2f} | "
            f"Gravité : {defect.severity}"
        )

    print("=" * 60)


def run():

    detections = receive_detections()

    db = SessionLocal()

    repository = Repository(db)

    for vehicle in detections:

        process_detection(vehicle)

        # ==========================================
        # Recherche ou création du véhicule
        # ==========================================

        existing_vehicle = repository.get_vehicle(vehicle.plate)

        if existing_vehicle:

            print(f"✅ Véhicule déjà enregistré : {vehicle.plate}")

            vehicle_db = existing_vehicle

        else:

            new_vehicle = Vehicle(

                owner_id=1,

                plate_number=vehicle.plate,

                brand=vehicle.brand,

                model=vehicle.model,

                year=vehicle.year,

                color="Unknown",

                fuel_type="Unknown",

                mileage=0,

                vin=None,

                vehicle_image=None,

                created_at=datetime.now(),

                updated_at=datetime.now()

            )

            repository.create_vehicle(new_vehicle)

            vehicle_db = new_vehicle

            print(f"🚗 Nouveau véhicule enregistré : {vehicle.plate}")

        # ==========================================
        # Création d'une inspection
        # ==========================================

        inspection = Inspection(

            vehicle_id=vehicle_db.id,

            inspection_date=datetime.strptime(
                vehicle.inspection_date,
                "%Y-%m-%d"
            ).date(),

            notes="Inspection automatique par RT-DETR",

            status="Completed",

            created_at=datetime.now()

        )

        repository.create_inspection(inspection)

        print(f"📝 Inspection créée (ID = {inspection.id})")

        # ==========================================
        # Enregistrement des défauts
        # ==========================================

        for detected_defect in vehicle.defects:

            defect = Defect(

                inspection_id=inspection.id,

                defect_name=detected_defect.type,

                confidence=detected_defect.confidence,

                severity=detected_defect.severity,

                description=f"{detected_defect.type} détecté automatiquement par RT-DETR.",

                solution="À compléter par le LLM.",

                defect_image=None,

                created_at=datetime.now()

            )

            repository.create_defect(defect)

            print(f"🔧 Défaut enregistré : {detected_defect.type}")

    db.close()

    print("\n✅ Toutes les données ont été enregistrées avec succès.")

if __name__ == "__main__":
    run()