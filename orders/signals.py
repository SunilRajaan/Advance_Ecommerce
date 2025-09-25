from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from notifications.utils import notify_user
# from delivery.models import Delivery
# from users.models import User

# @receiver(post_save, sender=Order)
# def create_delivery_on_order(sender, instance, created, **kwargs):
#     """
#     Creates a new Delivery object when an Order is created.
#     """
#     if created:
#         # Check if a Delivery object already exists for this order to prevent duplicates.
#         if not hasattr(instance, 'delivery'):
#             # Find a delivery person to assign the new delivery to
#             # It's best to filter out inactive users in a real-world scenario
#             delivery_person = User.objects.filter(role='delivery').first()

#             if delivery_person:
#                 Delivery.objects.create(order=instance, delivery_person=delivery_person)
#             else:
#                 # Handle the case where no delivery person exists
#                 print("No delivery person found to assign the new order to.")

@receiver(post_save, sender=Order)
def send_order_confirmation_notification(sender, instance, created, **kwargs):
    if created:
        notify_user(instance.customer, f"Your order #{instance.id} has been placed.", notif_type="order")

@receiver(post_save, sender=Order)
def send_order_confirmation_notification(sender, instance, created, **kwargs):
    if created:
        notify_user(instance.customer, f"Your order #{instance.id} has been placed.", notif_type="order")
