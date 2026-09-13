from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.decorators.csrf import csrf_exempt

from apps.reports.views import generate_report


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/",
        include("apps.users.urls")
    ),

    path(
        "api/",
        include("apps.defects.urls")
    ),

    path(
        "api/inspections/",
        include("apps.inspections.urls")
    ),

    path(
        "api/",
        include("apps.vehicles.urls")
    ),

    path(
        "api/reports/<int:inspection_id>/",
        csrf_exempt(generate_report),
        name="generate-report"
    ),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)