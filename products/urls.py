from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, CategoryListCreateView, SupplierDashboardView

urlpatterns = [
    path('dashboard/', SupplierDashboardView.as_view(), name='supplier-dashboard'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
]