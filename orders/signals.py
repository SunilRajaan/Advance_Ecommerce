from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from notifications.utils import notify_user
from .utils import send_order_confirmation_email
from delivery.models import Delivery
from users.models import User

@receiver(post_save, sender=Order)
def handle_order_creation_actions(sender, instance, created, **kwargs):
    """
    Consolidated signal handler for order creation:
    - Sends notification to customer
    - Sends confirmation email
    - Creates delivery for confirmed orders
    """
    if created:
        # 1. Internal Notification
        notify_user(instance.customer, f"Your order #{instance.id} has been placed.", notif_type="order")
        
        # 2. Email Confirmation
        send_order_confirmation_email(instance)

@receiver(post_save, sender=Order)
def create_delivery_for_confirmed_orders(sender, instance, **kwargs):
    """
    Create delivery automatically when order status changes to 'confirmed'
    """
    if instance.status == 'confirmed' and not hasattr(instance, 'delivery'):
        delivery_person = User.objects.filter(role='delivery', is_active=True).first()
        if delivery_person:
            Delivery.objects.create(order=instance, delivery_person=delivery_person)