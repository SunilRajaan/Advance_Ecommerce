from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category", write_only=True)
    supplier = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_id', 'price', 'stock', 'supplier']