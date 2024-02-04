from django.db import models


class Place(models.Model):
    name = models.CharField(
        'адрес',
        max_length=100,
        db_index=True,
        unique=True
    )
    lng = models.FloatField(
        'Долгота',
        null=True,
        blank=True
    )
    lat = models.FloatField(
        'Широта',
        null=True,
        blank=True
    )
