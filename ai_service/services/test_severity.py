from database.postgres import SessionLocal
from services.detection_service import detect_image


# ==========================================================
# CONFIGURATION
# ==========================================================

IMAGE_PATH = r"C:\Users\LENOVO\Downloads\Data_vechule\test_image.jpg"

# IMPORTANT :
# Mets ici un ID d'inspection qui existe réellement
INSPECTION_ID = 1


# ==========================================================
# CREATION SESSION DATABASE
# ==========================================================

db = SessionLocal()


try:

    print("========================================")
    print("TEST DETECTION + POSTGRESQL")
    print("========================================")

    print(
        f"Image : {IMAGE_PATH}"
    )

    print(
        f"Inspection ID : {INSPECTION_ID}"
    )

    # ======================================================
    # DETECTION
    # ======================================================

    results = detect_image(

        image_path=IMAGE_PATH,

        inspection_id=INSPECTION_ID,

        db=db,

        confidence_threshold=0.25
    )

    # ======================================================
    # RESULTAT
    # ======================================================

    print()
    print("========================================")
    print("RESULTAT DU TEST")
    print("========================================")

    for result in results:

        print()
        print(
            f"ID PostgreSQL : "
            f"{result['database_id']}"
        )

        print(
            f"Défaut : "
            f"{result['defect_name']}"
        )

        print(
            f"Confiance : "
            f"{result['confidence']:.2f}%"
        )

        print(
            f"Gravité : "
            f"{result['severity']}"
        )

        print(
            f"Position : "
            f"{result['location']}"
        )

    print()
    print("========================================")
    print("TEST TERMINE")
    print("========================================")


finally:

    db.close()