from django.db import models
from apps.vehicles.models import Vehicle


class Inspection(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="inspections"
    )

    inspection_date = models.DateField()

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=30,
        default="Completed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inspection #{self.id}"