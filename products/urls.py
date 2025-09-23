from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, CategoryListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
]