from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    ideal_quantity = models.FloatField()

class Food(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    quantity = models.FloatField()
    best_before = models.DateField()

    def __str__(self):
        return self.name