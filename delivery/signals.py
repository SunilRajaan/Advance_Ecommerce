from django.db.models.signals import post_save
from django.dispatch import receiver
from delivery.models import Delivery
from notifications.utils import notify_user

@receiver(post_save, sender=Delivery)
def delivery_assignment_notification(sender, instance, created, **kwargs):
    if created:
        notify_user(instance.delivery_person, f"New delivery assigned: Order #{instance.order.id}", notif_type="delivery")

    if not created:
        # Notify the customer when the delivery status changes to a key milestone.
        if instance.status in ['shipped', 'delivered']:
            notify_user(instance.order.customer, f"Your order #{instance.order.id} is now {instance.get_status_display()}.", notif_type="delivery")

@receiver(post_save, sender=Delivery)
def delivery_status_notification(sender, instance, created, **kwargs):
    # This part handles the initial notification to the delivery person.
    if created:
        notify_user(instance.delivery_person, f"New delivery assigned: Order #{instance.order.id}", notif_type="delivery")

    # This is the new part that notifies the customer.
    else:
        if instance.status in ['delivered']:
            notify_user(instance.order.customer, f"Your order #{instance.order.id} has been delivered.", notif_type="delivery")