from django.urls import path
from .views import RegisterView, LoginView, UserListView, UserDetailView, UserDeleteView, UserUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'), # Read (GET one)
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'), # Update (PUT/PATCH)
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'), # Delete (DELETE)
]