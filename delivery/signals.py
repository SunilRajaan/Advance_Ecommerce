from django.db.models.signals import post_save
from django.dispatch import receiver
from delivery.models import Delivery
from notifications.utils import notify_user
from orders.utils import send_delivery_status_email

@receiver(post_save, sender=Delivery)
def handle_delivery_notifications(sender, instance, created, **kwargs):
    """
    Consolidated signal handler for delivery notifications:
    - Notifies delivery person on assignment
    - Notifies customer on status changes
    - Sends email updates
    """
    if created:
        # Notify delivery person about new assignment
        notify_user(
            instance.delivery_person, 
            f"New delivery assigned: Order #{instance.order.id}", 
            notif_type="delivery"
        )
    
    else:
        # Notify customer about important status changes
        if instance.status in ['picked', 'in_transit', 'delivered']:
            status_display = instance.get_status_display()
            notify_user(
                instance.order.customer,
                f"Your order #{instance.order.id} is now {status_display}.",
                notif_type="delivery"
            )
        
        # Send email for major status updates
        if instance.status in ['shipped', 'delivered']:
            send_delivery_status_email(instance)