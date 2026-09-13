from django.urls import path

from .views import RecentInspectionsView, inspection_statistics


urlpatterns = [

    path(
        "recent/",
        RecentInspectionsView.as_view(),
        name="recent-inspections",
    ),

    path(
        "statistics/",
        inspection_statistics,
        name="inspection-statistics",
    ),

]