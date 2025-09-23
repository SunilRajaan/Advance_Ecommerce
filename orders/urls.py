from django.urls import path
from .views import OrderListCreateView, OrderRetrieveUpdateView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderRetrieveUpdateView.as_view(), name='order-detail'),
]