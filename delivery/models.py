from django.db import models
from users.models import User
from orders.models import Order

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked', 'Picked'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id} - {self.status}"