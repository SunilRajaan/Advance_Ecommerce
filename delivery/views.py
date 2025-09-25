from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Delivery
from .serializers import DeliverySerializer
from django.utils import timezone

class DeliveryListView(generics.ListAPIView):
    """
    List all deliveries assigned to the logged-in delivery personnel.
    """
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "delivery":
            return Delivery.objects.filter(delivery_person=user).order_by('-id')
        elif user.role == "admin":
            return Delivery.objects.all()
        return Delivery.objects.none()

class DeliveryUpdateView(generics.UpdateAPIView):
    """
    Update delivery status (delivery personnel only).
    """
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "delivery":
            return Delivery.objects.filter(delivery_person=user)
        elif user.role == "admin":
            return Delivery.objects.all()
        return Delivery.objects.none()
    
    def perform_update(self, serializer):
        # Automatically set delivered_at timestamp if status is 'delivered'
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'delivered':
            serializer.validated_data['delivered_at'] = timezone.now()
        
        serializer.save()

class DeliveryCreateView(generics.CreateAPIView):
    """
    Create a new delivery. Accessible to admin users only.
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        # Explicitly check for an existing delivery for the order
        order_id = request.data.get('order')
        if order_id and Delivery.objects.filter(order_id=order_id).exists():
            return Response(
                {"order": ["A delivery for this order already exists."]},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)