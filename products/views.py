from rest_framework import generics, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .analytics import get_supplier_dashboard_stats

class ProductPagination(PageNumberPagination):
    page_size = 10


class SupplierDashboardView(APIView):
    """
    Retrieve key analytics for the supplier dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'supplier':
            return Response({"detail": "Access denied. Must be a supplier."}, status=403)
            
        stats = get_supplier_dashboard_stats(user)
        return Response(stats)


class ProductListCreateView(generics.ListCreateAPIView):
    """
    List all products or create a new product.
    Filtering by name, category, and price is supported.
    """
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'price']
    ordering_fields = ['price', 'stock']
    permission_classes = [permissions.IsAuthenticated] # Add this line

    def get_queryset(self):
        # Customers: only active products. Suppliers/Admin: all their products.
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_authenticated:
            if user.role == "supplier":
                return queryset.filter(supplier=user)
            elif user.role == "customer":
                return queryset.filter(stock__gt=0)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the supplier to the current authenticated user
        serializer.save(supplier=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product.
    Suppliers can only manage their own products.
    """
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == "supplier":
            return queryset.filter(supplier=user)
        return queryset

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer