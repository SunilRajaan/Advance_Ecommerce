from django.urls import path
from .views import DeliveryListView, DeliveryUpdateView

urlpatterns = [
    path('', DeliveryListView.as_view(), name='delivery-list'),
    path('<int:pk>/', DeliveryUpdateView.as_view(), name='delivery-update'),
]