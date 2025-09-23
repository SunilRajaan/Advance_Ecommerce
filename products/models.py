from django.db import models
from users.models import User

class Category(models.Model):
    """Product categories: Electronics, Clothing, etc."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model with inventory tracking and supplier relationship."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name} ({self.category.name})"