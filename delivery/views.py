from rest_framework import generics, permissions
from .models import Delivery
from .serializers import DeliverySerializer

class DeliveryListView(generics.ListAPIView):
    """
    List all deliveries assigned to the logged-in delivery personnel.
    """
    serializer_class = DeliverySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "delivery":
            return Delivery.objects.filter(delivery_person=user)
        elif user.role == "admin":
            return Delivery.objects.all()
        return Delivery.objects.none()

class DeliveryUpdateView(generics.UpdateAPIView):
    """
    Update delivery status (delivery personnel only).
    """
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "delivery":
            return Delivery.objects.filter(delivery_person=user)
        elif user.role == "admin":
            return Delivery.objects.all()
        return Delivery.objects.none()