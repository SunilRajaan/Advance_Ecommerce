from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_price', 'created_at',)
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)