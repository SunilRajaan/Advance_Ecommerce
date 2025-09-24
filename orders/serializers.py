from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'total_price', 'created_at', 'updated_at', 'items']
        read_only_fields = ['status', 'total_price', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Check for sufficient stock
            if product.stock < quantity:
                raise serializers.ValidationError(f"Insufficient stock for product: {product.name}")

            # Calculate price and create OrderItem
            price = product.price * quantity
            OrderItem.objects.create(order=order, price=price, **item_data)

            # Update product stock
            product.stock -= quantity
            product.save()

            total_price += price

        order.total_price = total_price
        order.save()

        return order
    
    def update(self, instance, validated_data):
        # Handle regular fields (status in this case)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        
        # If you need to update order items in the future, handle items_data here
        # But for now, we'll ignore nested writes on update since items are write_only
        # and typically order items shouldn't be modified after creation
        
        return instance