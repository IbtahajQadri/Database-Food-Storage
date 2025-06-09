from django.db import models
from datetime import date

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    ideal_quantity = models.FloatField()

    def __str__(self):
        return self.name
    
    @property
    def current_quantity(self):
        """Calculate current total quantity of items in this category"""
        return self.foods.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def quantity_difference(self):
        """Calculate difference between ideal and current quantity"""
        return self.current_quantity - self.ideal_quantity
    
    @property
    def is_low_stock(self):
        """Check if category is below ideal stock level"""
        return self.current_quantity < self.ideal_quantity

class Food(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    quantity = models.FloatField()
    best_before = models.DateField()

    def __str__(self):
        return self.name
    

    @property
    def days_until_expiry(self):
        """Calculate days until the item expires"""
        today = date.today()
        return (self.best_before - today).days if self.best_before else 0
    
    @property
    def is_expired(self):
        """Check if the item has expired"""
        return self.best_before < date.today() if self.best_before else False
    
    @property
    def is_expiring_soon(self, days=7):
        """Check if item is expiring within specified days (default 7)"""
        return 0 <= self.days_until_expiry <= days
    
    @property
    def expiry_status(self):
        """Get a human-readable expiry status"""
        days = self.days_until_expiry
        if days < 0:
            return "Expired"
        elif days == 0:
            return "Expires Today"
        elif days <= 7:
            return f"Expires in {days} day{'s' if days != 1 else ''}"
        else:
            return "Fresh"
