from django.urls import path
from .views import DeliveryListView, DeliveryUpdateView, DeliveryCreateView

urlpatterns = [
    path('', DeliveryListView.as_view(), name='delivery-list'),
    path('create/', DeliveryCreateView.as_view(), name='delivery-create'),
    path('<int:pk>/', DeliveryUpdateView.as_view(), name='delivery-update'),
]