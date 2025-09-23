from django.db import models
from users.models import User

class Notification(models.Model):
    """
    Notification for users (real-time or email).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, default="general") # e.g. 'order', 'delivery', 'system'

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"