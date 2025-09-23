from .models import Product
from orders.models import OrderItem, Order
from delivery.models import Delivery
from django.db.models import Sum, Count

def get_supplier_dashboard_stats(user):
    # Products and stock
    products = Product.objects.filter(supplier=user)
    low_stock = products.filter(stock__lt=5)
    total_products = products.count()

    # Delivered orders for supplier's products
    delivered_items = (
        OrderItem.objects.filter(product__supplier=user, order__status='delivered')
        .aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
    )

    # Delivery status
    deliveries = Delivery.objects.filter(order__items__product__supplier=user)
    delivery_status_counts = deliveries.values('status').annotate(count=Count('id'))

    return {
        "total_products": total_products,
        "low_stock": list(low_stock.values('name', 'stock')),
        "delivered_items": delivered_items,
        "delivery_status_counts": list(delivery_status_counts),
    }