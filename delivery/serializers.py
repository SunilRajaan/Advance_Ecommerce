from rest_framework import serializers
from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.username', read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'order_id', 'delivery_person', 'delivery_person_name', 'status', 'assigned_at', 'delivered_at']