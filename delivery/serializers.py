from rest_framework import serializers
from .models import Delivery
from orders.models import Order
from users.models import User

class DeliverySerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.username', read_only=True)
    
    # Use PrimaryKeyRelatedField for writable fields, pointing to the correct models
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), write_only=True)
    delivery_person = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='delivery'), write_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_person', 'status', 'assigned_at', 'delivered_at', 'order_id', 'delivery_person_name']
        read_only_fields = ['id', 'assigned_at', 'delivered_at']