from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from django.core.mail import send_mail

@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, **kwargs):
    if created:
        # Order confirmation
        send_mail(
            subject="Order Confirmation",
            message=f"Your order #{instance.id} has been placed successfully.",
            from_email="noreply@ecommerce.com",
            recipient_list=[instance.customer.email],
        )
    else:
        # Delivery update
        if instance.status in ('shipped', 'delivered'):
            send_mail(
                subject=f"Order Update: {instance.status.title()}",
                message=f"Your order #{instance.id} is now {instance.status}.",
                from_email="noreply@ecommerce.com",
                recipient_list=[instance.customer.email],
            )