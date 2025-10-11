from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    """Sends an email to the customer upon order creation."""
    try:
        subject = f"Order Confirmation: Your Order #{order.id} is Placed!"
        message = (
            f"Dear {order.customer.username},\n\n"
            f"Thank you for your order! Your total is ${order.total_price}.\n"
            f"Your order status is currently: {order.status.capitalize()}.\n"
            f"We will notify you when it ships.\n\n"
            f"Ecommerce Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL, # Must be configured in settings.py
            [order.customer.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log the error, but don't fail the request
        print(f"Error sending email for order {order.id}: {e}")


def send_delivery_status_email(delivery):
    """Send email to customer when delivery status updates"""
    try:
        if delivery.status in ['shipped', 'delivered']:
            subject = f"Order #{delivery.order.id} {delivery.status.capitalize()}"
            message = (
                f"Dear {delivery.order.customer.username},\n\n"
                f"Your order #{delivery.order.id} is now {delivery.status}.\n"
                f"Total: ${delivery.order.total_price}\n\n"
                f"Thank you for shopping with us!"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [delivery.order.customer.email],
                fail_silently=False,
            )
    except Exception as e:
        print(f"Error sending delivery email: {e}")