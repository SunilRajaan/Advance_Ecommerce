from rest_framework import generics, filters, permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer

class OrderPagination(PageNumberPagination):
    page_size = 10
 
class OrderListCreateView(generics.ListCreateAPIView):
    """
    List all orders (Admin) or create order (Customer).
    Admin can filter by status or customer.
    """
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['status']
    filterset_fields = ['status', 'customer']
    ordering_fields = ['created_at', 'total_price']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_authenticated:
            if user.role == "customer":
                return queryset.filter(customer=user)
            elif user.role == "admin":
                return queryset
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class OrderRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update order status.
    Only Admin/Delivery Personnel can update status; customers can retrieve their own orders.
    """
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == "customer":
            return queryset.filter(customer=user)
        elif user.role in ("admin", "delivery"):
            return queryset
        return Order.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ("admin", "delivery"):
            raise serializers.ValidationError("You do not have permission to update orders")
        serializer.save()

class OrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        order_pk = self.kwargs['pk']
        user = self.request.user
        if user.role == "admin":
            return OrderItem.objects.filter(order__pk=order_pk)
        return OrderItem.objects.filter(order__pk=order_pk, order__customer=user)