from django.db import models
from apps.inspections.models import Inspection


class Defect(models.Model):

    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name="defects"
    )

    defect_name = models.CharField(
        max_length=100
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    confidence = models.FloatField()

    severity = models.CharField(
        max_length=30
    )

    description = models.TextField()

    solution = models.TextField()

    defect_image = models.ImageField(
        upload_to="defects/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.defect_name