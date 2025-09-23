from django.core.mail import send_mail
from .models import Product
from users.models import User

def batch_notify_low_stock():
    # Find all suppliers with low-stock products
    suppliers = User.objects.filter(role='supplier')
    for supplier in suppliers:
        low_stock_products = Product.objects.filter(supplier=supplier, stock__lt=5)
        if low_stock_products.exists():
            product_list = "\n".join([f"{p.name} (Stock: {p.stock})" for p in low_stock_products])
            send_mail(
                subject="Low Stock Alert",
                message=f"Dear {supplier.username},\n\nThe following products are low in stock:\n{product_list}\n\nPlease restock soon.",
                from_email="noreply@ecommerce.com",
                recipient_list=[supplier.email],
            )