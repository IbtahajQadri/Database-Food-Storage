from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)
    ideal_quantity = models.FloatField()

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    quantity = models.FloatField()
    best_before = models.DateField()

    def __str__(self):
        return self.name