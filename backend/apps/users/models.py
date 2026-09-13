from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # On utilise l'email pour la connexion
    username = None

    email = models.EmailField(unique=True)

    city = models.CharField(max_length=100)

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email