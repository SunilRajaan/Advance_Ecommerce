from django.urls import path
from .views import NotificationListView, NotificationMarkReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]