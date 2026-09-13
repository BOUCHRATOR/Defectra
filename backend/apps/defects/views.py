import requests

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.vehicles.models import Vehicle


class DetectionView(APIView):

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get(self, request):

        return JsonResponse({
            "success": True,
            "message": "Endpoint detection fonctionne"
        })

    def post(self, request):

        print("\n======================================")
        print("DJANGO - DETECTION")
        print("======================================")

        # ==================================================
        # 1. RECUPERER LE FICHIER
        # ==================================================

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:

            return JsonResponse({
                "success": False,
                "message": "Aucun fichier reçu par Django."
            }, status=400)

        print("Fichier reçu :", uploaded_file.name)
        print("Type :", uploaded_file.content_type)

        # ==================================================
        # 2. RECUPERER INFORMATIONS VEHICULE
        # ==================================================

        brand = str(
            request.data.get("brand", "")
        ).strip()

        model = str(
            request.data.get("model", "")
        ).strip()

        plate_number = str(
            request.data.get("plate_number", "")
        ).strip()

        print("\n===== INFORMATIONS VEHICULE =====")

        print("Marque :", brand)
        print("Modèle :", model)
        print("Plaque :", plate_number)

        # ==================================================
        # 3. VALIDATION
        # ==================================================

        if not plate_number:

            return JsonResponse({
                "success": False,
                "message": "La plaque est obligatoire."
            }, status=400)

        # ==================================================
        # 4. RECUPERER OU CREER VEHICULE
        # ==================================================

        try:

            vehicle = Vehicle.objects.filter(
                plate_number=plate_number
            ).first()

            if vehicle:

                print("\nVéhicule existant trouvé.")
                print("Vehicle ID :", vehicle.id)

                # Mise à jour uniquement si les valeurs
                # sont fournies

                if brand:
                    vehicle.brand = brand

                if model:
                    vehicle.model = model

                vehicle.save()

            else:

                print("\nNouveau véhicule.")

                vehicle = Vehicle.objects.create(
                    plate_number=plate_number,
                    brand=brand,
                    model=model
                )

                print(
                    "Nouveau Vehicle ID :",
                    vehicle.id
                )

        except Exception as e:

            print(
                "ERREUR VEHICULE :",
                str(e)
            )

            return JsonResponse({

                "success": False,

                "message":
                    "Impossible d'enregistrer le véhicule.",

                "error":
                    str(e)

            }, status=500)

        # ==================================================
        # 5. PREPARER FICHIER POUR FASTAPI
        # ==================================================
        #
        # IMPORTANT :
        #
        # FastAPI attend :
        #
        # image = fichier
        #
        # et NON "file"
        #
        # ==================================================

        uploaded_file.seek(0)

        files = {

            "file": (
                uploaded_file.name,
                uploaded_file.read(),
                uploaded_file.content_type
            )

        }

        # ==================================================
        # 6. PREPARER VEHICLE_ID POUR FASTAPI
        # ==================================================
        #
        # FastAPI attend :
        #
        # vehicle_id
        #
        # ==================================================

        data = {

            "vehicle_id": str(
                vehicle.id
            )

        }

        # ==================================================
        # 7. DEBUG
        # ==================================================

        print()
        print("===== DONNEES ENVOYEES A FASTAPI =====")

        print(
            "Vehicle ID :",
            vehicle.id
        )

        print(
            "Plate number :",
            vehicle.plate_number
        )

        print(
            "Brand :",
            vehicle.brand
        )

        print(
            "Model :",
            vehicle.model
        )

        print(
            "File :",
            uploaded_file.name
        )

        print(
            "File size :",
            len(files["file"][1]),
            "bytes"
        )

        print(
            "FastAPI URL :",
            "http://127.0.0.1:8001/defects/detect"
        )

        print("======================================")

        # ==================================================
        # 8. ENVOYER A FASTAPI
        # ==================================================

        try:

            response = requests.post(

                "http://127.0.0.1:8001/defects/detect",

                files=files,

                data=data,

                timeout=180

            )

        except requests.exceptions.RequestException as e:

            print()
            print("======================================")
            print("ERREUR CONNEXION FASTAPI")
            print(str(e))
            print("======================================")

            return JsonResponse({

                "success": False,

                "message":
                    "Impossible de contacter FastAPI.",

                "error":
                    str(e)

            }, status=502)

        # ==================================================
        # 9. REPONSE FASTAPI
        # ==================================================

        print()
        print("===== REPONSE FASTAPI =====")

        print(
            "Status FastAPI :",
            response.status_code
        )

        print(
            response.text
        )

        print("======================================")

        # ==================================================
        # 10. ERREUR FASTAPI
        # ==================================================

        if response.status_code != 200:

            return JsonResponse({

                "success": False,

                "message":
                    "FastAPI a retourné une erreur.",

                "fastapi_status":
                    response.status_code,

                "fastapi_response":
                    response.text

            }, status=502)

        # ==================================================
        # 11. PARSER JSON
        # ==================================================

        try:

            result = response.json()

        except Exception:

            return JsonResponse({

                "success": False,

                "message":
                    "FastAPI n'a pas retourné du JSON.",

                "raw_response":
                    response.text

            }, status=502)

        # ==================================================
        # 12. INFORMATIONS VEHICULE
        # ==================================================

        result["vehicle"] = {

            "id":
                vehicle.id,

            "brand":
                vehicle.brand,

            "model":
                vehicle.model,

            "plate_number":
                vehicle.plate_number

        }

        # ==================================================
        # 13. RETOUR FRONTEND
        # ==================================================

        return JsonResponse(
            result,
            status=200
        )