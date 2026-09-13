from django.urls import path

from .views import (
    get_vehicles,
    vehicle_detail
)


urlpatterns = [

    path(
        "vehicles/",
        get_vehicles,
        name="get_vehicles"
    ),

    path(
        "vehicles/<int:vehicle_id>/",
        vehicle_detail,
        name="vehicle-detail"
    ),

]