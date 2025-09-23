from django.db.models.signals import post_save
from django.dispatch import receiver
from delivery.models import Delivery
from notifications.utils import notify_user

@receiver(post_save, sender=Delivery)
def delivery_assignment_notification(sender, instance, created, **kwargs):
    if created:
        notify_user(instance.delivery_person, f"New delivery assigned: Order #{instance.order.id}", notif_type="delivery")