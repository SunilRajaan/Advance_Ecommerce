from notifications.models import Notification
from users.models import User

def notify_user(user, message, notif_type="general"):
    Notification.objects.create(user=user, message=message, type=notif_type)

def bulk_notify_delivery_assign(delivery_person, deliveries):
    msg = f"You have {len(deliveries)} new deliveries assigned."
    Notification.objects.create(user=delivery_person, message=msg, type="delivery")