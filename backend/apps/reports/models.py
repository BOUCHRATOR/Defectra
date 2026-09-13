from django.db import models
from apps.inspections.models import Inspection


class Report(models.Model):

    inspection = models.OneToOneField(
        Inspection,
        on_delete=models.CASCADE
    )

    summary = models.TextField()

    overall_condition = models.CharField(max_length=50)

    recommendation = models.TextField()

    pdf_file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id}"