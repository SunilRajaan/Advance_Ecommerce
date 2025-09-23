from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('delivery/', include("delivery.urls")),
    path('notifications/', include("notifications.urls")),
    path('orders/', include("orders.urls")),
    path('products/', include("products.urls")),
    path('users/', include("users.urls")),
]
