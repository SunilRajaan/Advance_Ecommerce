# notifications/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationModelTestCase(TestCase):
    """Test Notification model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123', role='customer')
    
    def test_create_notification(self):
        """Test notification creation"""
        notification = Notification.objects.create(
            user=self.user,
            message='Test notification message',
            type='general'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, 'Test notification message')
        self.assertEqual(notification.type, 'general')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
        
        self.assertEqual(str(notification), f'Notification for {self.user.username}: Test notification messa...')
    
    def test_notification_truncation(self):
        """Test notification string truncation"""
        long_message = 'A' * 100  # Very long message
        notification = Notification.objects.create(user=self.user, message=long_message)
        
        # String representation should be truncated
        self.assertTrue(len(str(notification)) < 50)

class NotificationAPITestCase(APITestCase):
    """Test Notification API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass123', role='customer')
        self.user2 = User.objects.create_user(username='user2', password='pass123', role='customer')
        
        # Create test notifications
        self.notification1 = Notification.objects.create(user=self.user1, message='Message 1')
        self.notification2 = Notification.objects.create(user=self.user1, message='Message 2')
        self.notification3 = Notification.objects.create(user=self.user2, message='Message 3')
    
    def test_list_notifications_authenticated(self):
        """Test user can list their own notifications"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Notifications should be ordered by creation date (newest first)
        self.assertEqual(response.data['results'][0]['id'], self.notification2.id)
        self.assertEqual(response.data['results'][1]['id'], self.notification1.id)
    
    def test_list_notifications_unauthenticated(self):
        """Test unauthenticated user cannot access notifications"""
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_mark_notification_as_read(self):
        """Test user can mark notification as read"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f'/notifications/{self.notification1.id}/', {'is_read': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
    
    def test_cannot_mark_others_notifications(self):
        """Test user cannot mark another user's notification as read"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f'/notifications/{self.notification3.id}/', {'is_read': True})
        
        # Should return 404 since user1 cannot access user2's notification
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        self.notification3.refresh_from_db()
        self.assertFalse(self.notification3.is_read)

class NotificationUtilsTestCase(TestCase):
    """Test notification utility functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123', role='customer')
        self.delivery_user = User.objects.create_user(username='delivery', password='test123', role='delivery')
    
    def test_notify_user_function(self):
        """Test the notify_user utility function"""
        from .utils import notify_user
        
        # Create notification using utility function
        notify_user(self.user, 'Test message', 'order')
        
        # Check if notification was created
        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.message, 'Test message')
        self.assertEqual(notification.type, 'order')
    
    def test_bulk_notify_delivery_assign(self):
        """Test bulk notification for delivery assignments"""
        from .utils import bulk_notify_delivery_assign
        
        # Mock delivery count
        delivery_count = 5
        bulk_notify_delivery_assign(self.delivery_user, range(delivery_count))
        
        # Check if notification was created
        notification = Notification.objects.filter(user=self.delivery_user).first()
        self.assertIsNotNone(notification)
        self.assertIn(f'{delivery_count} new deliveries', notification.message)
        self.assertEqual(notification.type, 'delivery')