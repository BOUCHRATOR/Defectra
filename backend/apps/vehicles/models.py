from django.db import models
from django.conf import settings


class Vehicle(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    plate_number = models.CharField(
        max_length=20,
        unique=True
    )

    brand = models.CharField(
        max_length=100
    )

    model = models.CharField(
        max_length=100
    )

    year = models.PositiveIntegerField()

    color = models.CharField(
        max_length=50
    )

    fuel_type = models.CharField(
        max_length=50
    )

    mileage = models.PositiveIntegerField()

    vin = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    vehicle_image = models.ImageField(
        upload_to="vehicles/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.brand} {self.model} - {self.plate_number}"