# ==========================================================
# services/detection_service.py
# ==========================================================

import os
import cv2

from ultralytics import RTDETR
from sqlalchemy.orm import Session

from database.models import Defect
from services.severity_service import evaluate_severity


# ==========================================================
# CHARGEMENT DU MODELE
# ==========================================================

MODEL_PATH = r"C:\Users\LENOVO\Downloads\Data_vechule\best.pt"

print("========================================")
print("CHARGEMENT DU MODELE RT-DETR")
print("========================================")

model = RTDETR(MODEL_PATH)

print("Modèle RT-DETR chargé.")
print("========================================")


# ==========================================================
# POSITION DU DEFAUT
# ==========================================================

def determine_location(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height
):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Horizontal
    if center_x < image_width / 3:
        horizontal = "left"
    elif center_x < (2 * image_width / 3):
        horizontal = "center"
    else:
        horizontal = "right"

    # Vertical
    if center_y < image_height / 3:
        vertical = "top"
    elif center_y < (2 * image_height / 3):
        vertical = "middle"
    else:
        vertical = "bottom"

    return f"{vertical}-{horizontal}"


# ==========================================================
# DETECTION IMAGE
# ==========================================================

def detect_image(
    image_path: str,
    inspection_id: int,
    db: Session,
    annotated_image_path: str
):

    print("\n========================================")
    print("DEBUT DETECTION RT-DETR")
    print("========================================")

    print("Image originale       :", image_path)
    print("Inspection ID         :", inspection_id)
    print("Image annotée         :", annotated_image_path)

    # ======================================================
    # VERIFICATION IMAGE ORIGINALE
    # ======================================================

    if not image_path:
        raise ValueError("image_path est vide.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image originale introuvable : {image_path}"
        )

    # ======================================================
    # CREER DOSSIER IMAGE ANNOTEE
    # ======================================================

    annotated_dir = os.path.dirname(
        os.path.abspath(annotated_image_path)
    )

    os.makedirs(
        annotated_dir,
        exist_ok=True
    )

    # ======================================================
    # LECTURE IMAGE
    # ======================================================

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Impossible de lire l'image : {image_path}"
        )

    image_height, image_width = image.shape[:2]

    print(
        f"Dimensions image : "
        f"{image_width} x {image_height}"
    )

    # ======================================================
    # PREDICTION RT-DETR
    # ======================================================

    print("\n===== PREDICTION RT-DETR =====")

    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False
    )

    if not results:
        print("Aucune prédiction.")

        # Sauvegarder quand même l'image originale
        # comme image annotée sans box
        success = cv2.imwrite(
            annotated_image_path,
            image
        )

        if not success:
            raise IOError(
                "Impossible de sauvegarder l'image annotée."
            )

        return {
            "success": True,
            "defects": [],
            "annotated_image": annotated_image_path,
            "annotated_image_exists": os.path.exists(
                annotated_image_path
            )
        }

    result = results[0]

    # ======================================================
    # CREATION IMAGE ANNOTEE
    # ======================================================

    print("\n===== CREATION IMAGE ANNOTEE =====")

    annotated_image = result.plot()

    success = cv2.imwrite(
        annotated_image_path,
        annotated_image
    )

    if not success:
        raise IOError(
            f"cv2.imwrite() a échoué : "
            f"{annotated_image_path}"
        )

    # Vérification réelle
    if not os.path.exists(annotated_image_path):
        raise IOError(
            "L'image annotée n'a pas été créée."
        )

    file_size = os.path.getsize(
        annotated_image_path
    )

    print("Image annotée sauvegardée.")
    print("Path :", annotated_image_path)
    print("Taille :", file_size, "bytes")

    # ======================================================
    # LISTE DES DEFAUTS
    # ======================================================

    detected_defects = []

    # ======================================================
    # AUCUNE BOX
    # ======================================================

    if (
        result.boxes is None
        or len(result.boxes) == 0
    ):

        print("\nAucun défaut détecté.")

        return {
            "success": True,
            "defects": [],
            "annotated_image": annotated_image_path,
            "annotated_image_exists": True
        }

    # ======================================================
    # PARCOURIR LES BOXES
    # ======================================================

    for box in result.boxes:

        # --------------------------------------------------
        # CLASS ID
        # --------------------------------------------------

        class_id = int(
            box.cls.item()
        )

        # --------------------------------------------------
        # NOM CLASSE
        # --------------------------------------------------

        if hasattr(result, "names"):
            defect_name = result.names.get(
                class_id,
                str(class_id)
            )
        else:
            defect_name = str(class_id)

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        confidence = float(
            box.conf.item()
        )

        # --------------------------------------------------
        # BOUNDING BOX
        # --------------------------------------------------

        coordinates = box.xyxy[0].tolist()

        x1 = float(coordinates[0])
        y1 = float(coordinates[1])
        x2 = float(coordinates[2])
        y2 = float(coordinates[3])

        # --------------------------------------------------
        # POSITION
        # --------------------------------------------------

        location = determine_location(
            x1,
            y1,
            x2,
            y2,
            image_width,
            image_height
        )

        print("\n========================================")
        print("DEFAUT DETECTE")
        print("========================================")

        print("Défaut       :", defect_name)
        print(
            "Confiance    :",
            f"{confidence * 100:.2f}%"
        )
        print("Position     :", location)

        print(
            "Bounding box :",
            (x1, y1, x2, y2)
        )

        # ==================================================
        # ANALYSE SEVERITE
        # ==================================================

        print("\n===== ANALYSE SEVERITE =====")

        try:

            severity_result = evaluate_severity(
                defect_name=defect_name,
                confidence=confidence,
                location=location,
                bbox=(x1, y1, x2, y2)
            )

        except Exception as e:

            print(
                "Erreur severity service :",
                str(e)
            )

            severity_result = {
                "severity": "UNKNOWN",
                "description": "",
                "solution": "Inspection professionnelle recommandée.",
                "missing_information": []
            }

        print("\n===== RESULTAT SEVERITE =====")
        print(severity_result)

        # ==================================================
        # EXTRACTION
        # ==================================================

        severity = severity_result.get(
            "severity",
            "UNKNOWN"
        )

        description = severity_result.get(
            "description",
            ""
        )

        solution = severity_result.get(
            "solution",
            ""
        )

        missing_information = severity_result.get(
            "missing_information",
            []
        )

        # ==================================================
        # IMAGE DU DEFAUT
        # ==================================================
        #
        # On utilise l'image annotée comme image du défaut.
        #
        # IMPORTANT :
        # Si ton modèle Defect possède defect_image,
        # on lui donne le chemin de l'image annotée.
        #

        defect_db = Defect(
            inspection_id=inspection_id,
            defect_name=defect_name,
            confidence=confidence,
            severity=severity,
            description=description,
            solution=solution,
            defect_image=annotated_image_path,
            location=location,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2
        )

        db.add(defect_db)

        # ==================================================
        # FLUSH POUR RECUPERER ID
        # ==================================================

        db.flush()

        print(
            "Défaut enregistré PostgreSQL."
        )

        print(
            "Defect ID :",
            defect_db.id
        )

        # ==================================================
        # RESULTAT FRONTEND
        # ==================================================

        detected_defects.append({

            "id": defect_db.id,

            "defect_name": defect_name,

            "defect_class": defect_name,

            "confidence": confidence,

            "severity": severity,

            "description": description,

            "solution": solution,

            "missing_information":
                missing_information,

            "location": location,

            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,

            "defect_image":
                annotated_image_path
        })

    # ======================================================
    # FLUSH
    # ======================================================

    db.flush()

    # ======================================================
    # FIN
    # ======================================================

    print("\n========================================")
    print("FIN DETECTION")
    print("========================================")

    print(
        "Nombre de défauts :",
        len(detected_defects)
    )

    print(
        "Image annotée :",
        annotated_image_path
    )

    print(
        "Existe :",
        os.path.exists(annotated_image_path)
    )

    print("========================================")

    # ======================================================
    # RETOUR
    # ======================================================

    return {

        "success": True,

        "defects":
            detected_defects,

        "annotated_image":
            annotated_image_path,

        "annotated_image_exists":
            os.path.exists(
                annotated_image_path
            )
    }