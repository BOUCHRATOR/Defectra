from django.http import JsonResponse
from .models import Vehicle


# ==========================================================
# LISTE DES VEHICULES
# GET /api/vehicles/
# ==========================================================

def get_vehicles(request):

    vehicles = Vehicle.objects.all().order_by("-created_at")

    data = []

    for vehicle in vehicles:

        data.append({
            "id": vehicle.id,
            "plate_number": vehicle.plate_number,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
            "fuel_type": vehicle.fuel_type,
            "mileage": vehicle.mileage,
            "vin": vehicle.vin,

            "vehicle_image": (
                request.build_absolute_uri(
                    vehicle.vehicle_image.url
                )
                if vehicle.vehicle_image
                else None
            ),
        })

    return JsonResponse({
        "success": True,
        "vehicles": data
    })


# ==========================================================
# DETAILS D'UN VEHICULE
# GET /api/vehicles/74/
# ==========================================================

def vehicle_detail(request, vehicle_id):

    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)

    except Vehicle.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "Véhicule introuvable"
        }, status=404)


    # ======================================================
    # INSPECTIONS
    # ======================================================

    inspections_data = []

    # Tous les défauts du véhicule
    all_defects = []


    for inspection in vehicle.inspections.all().order_by("inspection_date"):

        defects_data = []


        # ==================================================
        # DEFAUTS DE CETTE INSPECTION
        # ==================================================

        for defect in inspection.defects.all():

            defect_data = {

                "id": defect.id,

                "defect_name": defect.defect_name,

                "confidence": defect.confidence,

                "severity": defect.severity,
                "location" : defect.location,

                "description": defect.description,

                "solution": defect.solution,
                "defect_image":defect.defect_image.url if defect.defect_image else None,

            }

            defects_data.append(defect_data)

            all_defects.append(defect_data)


        # ==================================================
        # CALCUL DE LA SEVERITE MOYENNE
        # ==================================================

        severities = []

        for defect in inspection.defects.all():

            try:

                severity_value = float(defect.severity)

                severities.append(severity_value)

            except (ValueError, TypeError):

                pass


        if severities:

            average_severity = sum(severities) / len(severities)

        else:

            average_severity = 0


        # ==================================================
        # INSPECTION
        # ==================================================

        inspections_data.append({

            "id": inspection.id,

            "date": inspection.inspection_date,

            "notes": inspection.notes,

            "status": inspection.status,

            "severity": round(average_severity, 2),

            "defects_count": len(defects_data),

            "defects": defects_data,

        })


    # ======================================================
    # REPONSE
    # ======================================================

    return JsonResponse({

        "success": True,

        "vehicle": {

            "id": vehicle.id,

            "plate_number": vehicle.plate_number,

            "brand": vehicle.brand,

            "model": vehicle.model,

            "year": vehicle.year,

            "color": vehicle.color,

            "fuel_type": vehicle.fuel_type,

            "mileage": vehicle.mileage,

            "vin": vehicle.vin,


            # IMAGE VEHICULE
            "vehicle_image": (

                request.build_absolute_uri(
                    vehicle.vehicle_image.url
                )

                if vehicle.vehicle_image

                else None

            ),


            # INSPECTIONS
            "inspections": inspections_data,


            # TOUS LES DEFAUTS
            "defects": all_defects,


            # NOMBRE TOTAL DE DEFAUTS
            "defects_count": len(all_defects),

        }

    })