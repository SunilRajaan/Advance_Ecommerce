from orders.models import Order, OrderItem
from products.models import Product
from .models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

def get_admin_dashboard_stats():
    # Total revenue from delivered orders
    total_revenue = Order.objects.filter(status='delivered').aggregate(sum=Sum('total_price'))['sum'] or 0

    # Orders by status
    order_status_counts = Order.objects.values('status').annotate(count=Count('id'))

    # Sales over last 30 days
    last_month = timezone.now() - timedelta(days=30)
    sales_last_month = Order.objects.filter(status='delivered', created_at__gte=last_month).aggregate(sum=Sum('total_price'))['sum'] or 0

    # Top-selling products (by quantity)
    top_products = (
        OrderItem.objects.values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    # Top suppliers by total sold
    top_suppliers = (
        Product.objects.values('supplier__username')
        .annotate(total_stock=Sum('stock'))
        .order_by('-total_stock')[:5]
    )

    # Inventory alerts
    low_stock_products = Product.objects.filter(stock__lt=5).values('name', 'supplier__username', 'stock')

    return {
        "total_revenue": total_revenue,
        "order_status_counts": list(order_status_counts),
        "sales_last_month": sales_last_month,
        "top_products": list(top_products),
        "top_suppliers": list(top_suppliers),
        "low_stock_products": list(low_stock_products),
    }