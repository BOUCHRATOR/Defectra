# ==========================================================
# apps/reports/views.py
# ==========================================================

import os
import shutil
import requests

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# ==========================================================
# FASTAPI
# ==========================================================

FASTAPI_URL = "http://127.0.0.1:8001"


# ==========================================================
# GENERATE REPORT
# ==========================================================

@csrf_exempt
def generate_report(request, inspection_id):

    print()
    print("======================================")
    print("DJANGO - GENERATION RAPPORT")
    print("======================================")

    print("Method :", request.method)
    print("Inspection ID :", inspection_id)

    # ======================================================
    # POST UNIQUEMENT
    # ======================================================

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Méthode POST requise."
            },
            status=405
        )

    # ======================================================
    # URL FASTAPI
    # ======================================================

    url = f"{FASTAPI_URL}/report/{inspection_id}"

    print("FastAPI URL :", url)

    # ======================================================
    # APPEL FASTAPI
    # ======================================================

    try:

        response = requests.post(
            url,
            timeout=180
        )

    except requests.exceptions.Timeout as e:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "FastAPI a mis trop de temps "
                    "à générer le rapport."
                ),
                "error": str(e)
            },
            status=504
        )

    except requests.exceptions.ConnectionError as e:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Impossible de contacter FastAPI."
                ),
                "error": str(e)
            },
            status=502
        )

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Erreur communication FastAPI."
                ),
                "error": str(e)
            },
            status=500
        )

    # ======================================================
    # REPONSE FASTAPI
    # ======================================================

    print()
    print("===== REPONSE FASTAPI =====")

    print(
        "Status :",
        response.status_code
    )

    print(
        "Content-Type :",
        response.headers.get(
            "Content-Type"
        )
    )

    print(
        "Body :",
        response.text[:3000]
    )

    # ======================================================
    # ERREUR FASTAPI
    # ======================================================

    if response.status_code != 200:

        try:

            error_data = response.json()

        except Exception:

            error_data = {
                "detail": response.text
            }

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Erreur génération rapport."
                ),
                "fastapi": error_data
            },
            status=response.status_code
        )

    # ======================================================
    # JSON FASTAPI
    # ======================================================

    try:

        data = response.json()

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "FastAPI a retourné "
                    "une réponse non JSON."
                ),
                "error": str(e),
                "raw_response": response.text
            },
            status=500
        )

    print()
    print("===== DONNEES RAPPORT =====")
    print(data)

    # ======================================================
    # RECUPERER LE CHEMIN DU PDF
    # ======================================================

    pdf_file = None

    if isinstance(data, dict):

        # Le PDF est actuellement ici :
        #
        # data["pdf_file"]
        #

        report_data = data.get(
            "report"
        )

        if isinstance(
            report_data,
            dict
        ):

            pdf_file = report_data.get(
                "pdf_file"
            )

        # sécurité : chercher aussi au niveau principal
        if not pdf_file:

            pdf_file = data.get(
                "pdf_file"
            )

    print()
    print("===== PDF FASTAPI =====")
    print("PDF file :", pdf_file)

    # ======================================================
    # VERIFIER PDF
    # ======================================================

    if not pdf_file:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "FastAPI a généré le rapport "
                    "mais n'a pas retourné "
                    "le chemin du PDF."
                ),
                "report": data
            },
            status=500
        )

    # Normaliser Windows
    pdf_file = str(
        pdf_file
    ).replace(
        "\\",
        os.sep
    )

    # ======================================================
    # VERIFIER EXISTENCE
    # ======================================================

    if not os.path.isfile(
        pdf_file
    ):

        print(
            "PDF INTROUVABLE :",
            pdf_file
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Le PDF retourné par FastAPI "
                    "n'existe pas sur le disque."
                ),
                "pdf_file": pdf_file
            },
            status=500
        )

    print(
        "✅ PDF FASTAPI EXISTE"
    )

    print(
        "Taille :",
        os.path.getsize(
            pdf_file
        ),
        "bytes"
    )

    # ======================================================
    # DOSSIER DJANGO MEDIA/REPORTS
    # ======================================================

    reports_dir = os.path.join(
        settings.MEDIA_ROOT,
        "reports"
    )

    os.makedirs(
        reports_dir,
        exist_ok=True
    )

    print()
    print("===== DOSSIER REPORTS DJANGO =====")

    print(
        "Reports dir :",
        reports_dir
    )

    # ======================================================
    # NOM DU PDF
    # ======================================================

    pdf_name = (
        f"inspection_{inspection_id}.pdf"
    )

    destination_pdf = os.path.join(
        reports_dir,
        pdf_name
    )

    # ======================================================
    # COPIER PDF
    # ======================================================

    try:

        shutil.copy2(
            pdf_file,
            destination_pdf
        )

    except Exception as e:

        print(
            "ERREUR COPIE PDF :",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Impossible de copier "
                    "le PDF vers backend/media/reports."
                ),
                "error": str(e)
            },
            status=500
        )

    # ======================================================
    # VERIFICATION COPIE
    # ======================================================

    if not os.path.isfile(
        destination_pdf
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Le PDF n'a pas été "
                    "copié correctement."
                )
            },
            status=500
        )

    print()
    print("✅ PDF COPIE DANS DJANGO")
    print(
        "Destination :",
        destination_pdf
    )

    print(
        "Taille :",
        os.path.getsize(
            destination_pdf
        ),
        "bytes"
    )

    # ======================================================
    # URL MEDIA DJANGO
    # ======================================================

    relative_pdf = os.path.relpath(
        destination_pdf,
        settings.MEDIA_ROOT
    ).replace(
        "\\",
        "/"
    )

    pdf_url = (
        settings.MEDIA_URL
        + relative_pdf
    )

    # ======================================================
    # URL COMPLETE
    # ======================================================

    pdf_url = request.build_absolute_uri(
        pdf_url
    )

    # ======================================================
    # REPONSE
    # ======================================================

    result = {

        "success": True,

        "inspection_id":
            inspection_id,

        "report":
            data,

        "pdf_file":
            relative_pdf,

        "pdf_url":
            pdf_url
    }

    print()
    print("======================================")
    print("PDF FINAL")
    print("======================================")

    print(
        "Fichier :",
        relative_pdf
    )

    print(
        "URL :",
        pdf_url
    )

    print("======================================")

    return JsonResponse(
        result,
        status=200
    )