# ==========================================================
# api/defect.py
# ==========================================================

import os
import uuid
import shutil

from pathlib import Path
from datetime import datetime

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from database.postgres import get_db
from database.models import Vehicle, Inspection

from services.detection_service import detect_image


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/defects",
    tags=["Defects"]
)


# ==========================================================
# CHEMINS DU PROJET
# ==========================================================

# ==========================================================
# STRUCTURE :
#
# Data_vechule/
#
# ├── ai_service/
# │   ├── api/
# │   ├── main.py
# │   └── ...
# │
# └── backend/
#     ├── manage.py
#     ├── media/
#     │   └── inspections/
#     │       ├── original/
#     │       └── annotated/
#     └── ...
#
# ==========================================================

# ai_service/
AI_SERVICE_DIR = Path(__file__).resolve().parent.parent

# Data_vechule/
PROJECT_DIR = AI_SERVICE_DIR.parent

# Data_vechule/backend/
BACKEND_DIR = PROJECT_DIR / "backend"

# Data_vechule/backend/media/
MEDIA_ROOT = BACKEND_DIR / "media"

# backend/media/inspections/
INSPECTIONS_DIR = MEDIA_ROOT / "inspections"

# backend/media/inspections/original/
ORIGINAL_DIR = INSPECTIONS_DIR / "original"

# backend/media/inspections/annotated/
ANNOTATED_DIR = INSPECTIONS_DIR / "annotated"


# ==========================================================
# CREATION DES DOSSIERS
# ==========================================================

MEDIA_ROOT.mkdir(
    parents=True,
    exist_ok=True
)

INSPECTIONS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ORIGINAL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ANNOTATED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# DEBUG DES CHEMINS
# ==========================================================

print()
print("========================================")
print("MEDIA CONFIGURATION")
print("========================================")

print("AI_SERVICE_DIR :")
print(AI_SERVICE_DIR)

print()

print("PROJECT_DIR :")
print(PROJECT_DIR)

print()

print("BACKEND_DIR :")
print(BACKEND_DIR)

print()

print("MEDIA_ROOT :")
print(MEDIA_ROOT)

print()

print("ORIGINAL_DIR :")
print(ORIGINAL_DIR)

print()

print("ANNOTATED_DIR :")
print(ANNOTATED_DIR)

print()

print("MEDIA EXISTS :",
      MEDIA_ROOT.exists())

print("ORIGINAL EXISTS :",
      ORIGINAL_DIR.exists())

print("ANNOTATED EXISTS :",
      ANNOTATED_DIR.exists())

print("========================================")
print()


# ==========================================================
# FONCTION CHEMIN RELATIF MEDIA
# ==========================================================

def get_media_relative_path(
    file_path: Path
) -> str:

    """
    Transforme :

    C:\\...\\backend\\media\\inspections\\annotated\\image.jpg

    en :

    inspections/annotated/image.jpg
    """

    relative_path = os.path.relpath(
        str(file_path),
        str(MEDIA_ROOT)
    )

    return relative_path.replace(
        "\\",
        "/"
    )


# ==========================================================
# ENDPOINT DETECTION
# ==========================================================

@router.post("/detect")
async def detect_defects(

    # Fichier envoyé par Django
    file: UploadFile = File(...),

    # ID du véhicule
    vehicle_id: int = Form(...),

    # Session PostgreSQL
    db: Session = Depends(get_db)

):

    print()
    print("========================================")
    print("FASTAPI - DETECTION")
    print("========================================")

    print("Vehicle ID :", vehicle_id)
    print("Filename   :", file.filename)
    print("ContentType:", file.content_type)

    # ======================================================
    # VERIFIER FICHIER
    # ======================================================

    if file is None:

        raise HTTPException(
            status_code=400,
            detail="Aucun fichier reçu."
        )

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Nom du fichier absent."
        )

    # ======================================================
    # VERIFIER EXTENSION
    # ======================================================

    original_filename = file.filename

    extension = Path(
        original_filename
    ).suffix.lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Format non supporté. "
                "Utilisez JPG, JPEG, PNG ou WEBP."
            )
        )

    # ======================================================
    # VERIFIER VEHICULE
    # ======================================================

    try:

        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.id == vehicle_id
            )
            .first()
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la recherche "
                f"du véhicule : {str(e)}"
            )
        )

    if vehicle is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Véhicule {vehicle_id} "
                "introuvable."
            )
        )

    print()
    print("Véhicule trouvé.")
    print("Vehicle ID :", vehicle.id)

    # ======================================================
    # IDENTIFIANT UNIQUE
    # ======================================================

    unique_id = uuid.uuid4().hex

    # ======================================================
    # NOMS DES FICHIERS
    # ======================================================

    original_name = (
        f"vehicle_{vehicle_id}_"
        f"{unique_id}"
        f"{extension}"
    )

    annotated_name = (
        f"vehicle_{vehicle_id}_"
        f"{unique_id}"
        "_annotated.jpg"
    )

    # ======================================================
    # CHEMINS PHYSIQUES
    # ======================================================

    original_path = (
        ORIGINAL_DIR
        / original_name
    )

    annotated_path = (
        ANNOTATED_DIR
        / annotated_name
    )

    print()
    print("===== CHEMINS IMAGES =====")

    print(
        "Original :",
        original_path
    )

    print(
        "Annotated :",
        annotated_path
    )

    # ======================================================
    # SAUVEGARDER IMAGE ORIGINALE
    # ======================================================

    try:

        # revenir au début du fichier
        await file.seek(0)

        with open(
            original_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Impossible de sauvegarder "
                f"l'image originale : {str(e)}"
            )
        )

    # ======================================================
    # VERIFICATION IMAGE ORIGINALE
    # ======================================================

    if not original_path.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                "L'image originale "
                "n'a pas été créée."
            )
        )

    print()
    print("✅ IMAGE ORIGINALE SAUVEGARDEE")
    print(
        "Path :",
        original_path
    )
    print(
        "Size :",
        original_path.stat().st_size,
        "bytes"
    )

    # ======================================================
    # CREER INSPECTION
    # ======================================================

    inspection = None

    try:

        inspection = Inspection(

            vehicle_id=vehicle_id,

            inspection_date=datetime.utcnow(),

            notes=(
                "Inspection automatique "
                "réalisée par le système IA."
            ),

            status="completed",

            created_at=datetime.utcnow()
        )

        db.add(inspection)

        db.flush()

        print()
        print("✅ INSPECTION CREEE")
        print(
            "Inspection ID :",
            inspection.id
        )

    except Exception as e:

        db.rollback()

        # supprimer image originale
        if original_path.exists():

            try:
                original_path.unlink()
            except Exception:
                pass

        print()
        print(
            "ERREUR CREATION INSPECTION :",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur création inspection : "
                f"{str(e)}"
            )
        )

    # ======================================================
    # DETECTION RT-DETR
    # ======================================================

    print()
    print("========================================")
    print("APPEL DETECTION RT-DETR")
    print("========================================")

    try:

        detection_result = detect_image(

            image_path=str(
                original_path
            ),

            inspection_id=inspection.id,

            db=db,

            annotated_image_path=str(
                annotated_path
            )
        )

    except Exception as e:

        db.rollback()

        # supprimer image originale
        if original_path.exists():

            try:
                original_path.unlink()
            except Exception:
                pass

        # supprimer image annotée
        if annotated_path.exists():

            try:
                annotated_path.unlink()
            except Exception:
                pass

        print()
        print(
            "ERREUR DETECTION :",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur pendant la détection : "
                f"{str(e)}"
            )
        )

    # ======================================================
    # VERIFIER IMAGE ANNOTEE
    # ======================================================

    print()
    print("========================================")
    print("VERIFICATION IMAGE ANNOTEE")
    print("========================================")

    print(
        "Path :",
        annotated_path
    )

    print(
        "Existe :",
        annotated_path.exists()
    )

    if annotated_path.exists():

        print(
            "Taille :",
            annotated_path.stat().st_size,
            "bytes"
        )

    if not annotated_path.exists():

        db.rollback()

        if original_path.exists():

            try:
                original_path.unlink()
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=(
                "La détection est terminée, "
                "mais l'image annotée "
                "n'existe pas."
            )
        )

    print(
        "✅ IMAGE ANNOTEE EXISTE"
    )

    # ======================================================
    # CHEMINS RELATIFS POUR LA DB
    # ======================================================

    original_relative = (
        get_media_relative_path(
            original_path
        )
    )

    annotated_relative = (
        get_media_relative_path(
            annotated_path
        )
    )

    print()
    print("========================================")
    print("CHEMINS RELATIFS")
    print("========================================")

    print(
        "Original relatif :",
        original_relative
    )

    print(
        "Annotated relatif :",
        annotated_relative
    )

    # ======================================================
    # ENREGISTRER IMAGE DU VEHICULE
    # ======================================================
    #
    # On cherche un champ image existant
    # dans le modèle Vehicle.
    #

    vehicle_image_field = None

    possible_vehicle_fields = [

        "image",

        "image_path",

        "vehicle_image",

        "vehicle_image_path",

        "photo",

        "photo_path"
    ]

    for field_name in possible_vehicle_fields:

        if hasattr(
            Vehicle,
            field_name
        ):

            vehicle_image_field = (
                field_name
            )

            break

    if vehicle_image_field:

        try:

            setattr(
                vehicle,
                vehicle_image_field,
                original_relative
            )

            print()
            print(
                "✅ IMAGE VEHICULE ENREGISTREE"
            )

            print(
                "Champ :",
                vehicle_image_field
            )

            print(
                "Valeur :",
                original_relative
            )

        except Exception as e:

            print(
                "Attention image Vehicle :",
                str(e)
            )

    else:

        print()
        print(
            "⚠️ Aucun champ image trouvé "
            "dans Vehicle."
        )

    # ======================================================
    # ENREGISTRER IMAGE DANS INSPECTION
    # ======================================================
    #
    # Si ton modèle Inspection possède
    # un champ image, on y met l'image annotée.
    #

    inspection_image_field = None

    possible_inspection_fields = [

        "image",

        "image_path",

        "inspection_image",

        "inspection_image_path",

        "annotated_image",

        "annotated_image_path",

        "result_image",

        "result_image_path"
    ]

    for field_name in possible_inspection_fields:

        if hasattr(
            Inspection,
            field_name
        ):

            inspection_image_field = (
                field_name
            )

            break

    if inspection_image_field:

        try:

            setattr(
                inspection,
                inspection_image_field,
                annotated_relative
            )

            print()
            print(
                "✅ IMAGE ANNOTEE INSPECTION "
                "ENREGISTREE"
            )

            print(
                "Champ :",
                inspection_image_field
            )

            print(
                "Valeur :",
                annotated_relative
            )

        except Exception as e:

            print(
                "Attention image Inspection :",
                str(e)
            )

    else:

        print()
        print(
            "⚠️ Aucun champ image trouvé "
            "dans Inspection."
        )

    # ======================================================
    # COMMIT FINAL
    # ======================================================

    try:

        db.commit()

        print()
        print("========================================")
        print("✅ POSTGRESQL COMMIT OK")
        print("========================================")

    except Exception as e:

        db.rollback()

        print()
        print(
            "ERREUR COMMIT POSTGRESQL :",
            str(e)
        )

        # On peut garder les fichiers pour debug,
        # mais on avertit l'appelant.
        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors du commit PostgreSQL : "
                f"{str(e)}"
            )
        )

    # ======================================================
    # URL RELATIVE POUR DJANGO
    # ======================================================

    original_media_url = (
        "/media/"
        + original_relative
    )

    annotated_media_url = (
        "/media/"
        + annotated_relative
    )

    # ======================================================
    # RESULTAT DETECTION
    # ======================================================

    defects = detection_result.get(
        "defects",
        []
    )

    # ======================================================
    # REPONSE
    # ======================================================

    response = {

        "success": True,

        "message": (
            "Détection terminée "
            "avec succès."
        ),

        "vehicle_id": vehicle.id,

        "inspection_id": inspection.id,

        # ----------------------------------------------
        # IMAGE ORIGINALE
        # ----------------------------------------------

        "original_image": {

            "path": original_relative,

            "url": original_media_url
        },

        # ----------------------------------------------
        # IMAGE ANNOTEE
        # ----------------------------------------------

        "annotated_image": {

            "path": annotated_relative,

            "url": annotated_media_url,

            "exists":
                annotated_path.exists()
        },

        # Pour faciliter le frontend
        "annotated_image_url":
            annotated_media_url,

        # ----------------------------------------------
        # DEFAUTS
        # ----------------------------------------------

        "defects": defects,

        # ----------------------------------------------
        # DEBUG
        # ----------------------------------------------

        "files": {

            "original_exists":
                original_path.exists(),

            "annotated_exists":
                annotated_path.exists(),

            "original_size":
                (
                    original_path.stat().st_size
                    if original_path.exists()
                    else 0
                ),

            "annotated_size":
                (
                    annotated_path.stat().st_size
                    if annotated_path.exists()
                    else 0
                )
        }
    }

    print()
    print("========================================")
    print("REPONSE FASTAPI")
    print("========================================")

    print(
        "Inspection :",
        inspection.id
    )

    print(
        "Original :",
        original_relative
    )

    print(
        "Annotated :",
        annotated_relative
    )

    print(
        "Annotated exists :",
        annotated_path.exists()
    )

    print(
        "Nombre défauts :",
        len(defects)
    )

    print("========================================")

    return response