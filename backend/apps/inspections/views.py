from django.http import JsonResponse
from django.db.models import Avg
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay

from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import Inspection
from apps.defects.models import Defect


# ==========================================================
# DERNIÈRES CONSULTATIONS
# ==========================================================

class RecentInspectionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        inspections = (
            Inspection.objects
            .select_related("vehicle")
            .prefetch_related("defects")
            .order_by("-created_at")[:10]
        )

        data = []

        for inspection in inspections:

            data.append({

                "id": inspection.id,

                "inspection_date": (
                    inspection.inspection_date.strftime("%d/%m/%Y")
                    if inspection.inspection_date
                    else None
                ),

                "status": inspection.status,

                "vehicle": {

                    "id": inspection.vehicle.id,

                    "brand": inspection.vehicle.brand,

                    "model": inspection.vehicle.model,

                    "plate_number": inspection.vehicle.plate_number,

                },

                "defects_count": inspection.defects.count(),

                "defects": [

                    {
                        "id": defect.id,
                        "defect_name": defect.defect_name,
                        "confidence": defect.confidence,
                        "severity": defect.severity,
                    }

                    for defect in inspection.defects.all()
                ],

            })

        return JsonResponse(
            data,
            safe=False
        )


# ==========================================================
# STATISTIQUES DU DASHBOARD
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inspection_statistics(request):

    # ======================================================
    # FILTRE
    # ======================================================

    period = request.GET.get(
        "period",
        "month"
    )

    today = timezone.localdate()


    # ======================================================
    # DATE DE DÉBUT
    # ======================================================

    if period == "today":

        start_date = today


    elif period == "week":

        start_date = (
            today -
            timedelta(days=today.weekday())
        )


    elif period == "month":

        start_date = today.replace(
            day=1
        )


    elif period == "quarter":

        quarter = (
            (today.month - 1) // 3
        )

        first_month = (
            quarter * 3 + 1
        )

        start_date = today.replace(
            month=first_month,
            day=1
        )


    elif period == "year":

        start_date = today.replace(
            month=1,
            day=1
        )


    else:

        start_date = today.replace(
            day=1
        )


    # ======================================================
    # INSPECTIONS
    # ======================================================

    inspections = Inspection.objects.filter(

        inspection_date__gte=start_date,

        inspection_date__lte=today

    )


    inspections_count = inspections.count()


    # ======================================================
    # VÉHICULES CONSULTÉS
    # ======================================================

    vehicles_consulted = (
        inspections
        .values("vehicle_id")
        .distinct()
        .count()
    )


    # ======================================================
    # DÉFAUTS
    # ======================================================

    defects = Defect.objects.filter(

        inspection__in=inspections

    )


    defects_count = defects.count()


    # ======================================================
    # DÉFAUTS GRAVES
    # ======================================================

    severe_defects = defects.filter(

        severity__iexact="High"

    ).count()


    # ======================================================
    # CONFIANCE MOYENNE IA
    # ======================================================

    average_confidence = defects.aggregate(

        avg=Avg("confidence")

    )["avg"]


    if average_confidence is None:

        average_confidence = 0


    # ======================================================
    # ÉVOLUTION DES INSPECTIONS
    # ======================================================

    if period == "today":

        chart_queryset = (
            inspections
            .values("inspection_date")
            .annotate(
                count=__import__(
                    "django.db.models",
                    fromlist=["Count"]
                ).Count("id")
            )
            .order_by("inspection_date")
        )

        chart = [

            {
                "date": item["inspection_date"].strftime(
                    "%d/%m"
                ),

                "count": item["count"]

            }

            for item in chart_queryset

        ]


    else:

        chart_queryset = (
            inspections
            .annotate(
                month=TruncMonth(
                    "inspection_date"
                )
            )
            .values("month")
            .annotate(
                count=__import__(
                    "django.db.models",
                    fromlist=["Count"]
                ).Count("id")
            )
            .order_by("month")
        )

        chart = [

            {
                "date": item["month"].strftime(
                    "%b"
                ),

                "count": item["count"]

            }

            for item in chart_queryset

        ]


    # ======================================================
    # DÉFAUTS PAR SÉVÉRITÉ
    # ======================================================

    severity_data = {}

    for defect in defects:

        severity = defect.severity or "Unknown"

        if severity not in severity_data:

            severity_data[severity] = 0

        severity_data[severity] += 1


    severity_chart = [

        {
            "severity": severity,

            "count": count

        }

        for severity, count
        in severity_data.items()

    ]


    # ======================================================
    # RÉPONSE
    # ======================================================

    return JsonResponse({

        "success": True,

        "period": period,

        "vehicles_consulted":
            vehicles_consulted,

        "inspections":
            inspections_count,

        "defects":
            defects_count,

        "severe_defects":
            severe_defects,

        "average_confidence":
            round(
                average_confidence,
                2
            ),

        "chart":
            chart,

        "severity_chart":
            severity_chart,

    })