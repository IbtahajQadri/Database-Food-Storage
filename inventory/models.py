from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)
    ideal_quantity = models.FloatField()

    def __str__(self):
        return self.name


