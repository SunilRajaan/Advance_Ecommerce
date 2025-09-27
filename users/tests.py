# users/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserModelTestCase(TestCase):
    """Test User model functionality"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'customer'
        }
    
    def test_create_user(self):
        """Test user creation with different roles"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'customer')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_superuser(self):
        """Test superuser creation"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, 'customer')  # Default role
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser (customer)')

class UserAPITestCase(APITestCase):
    """Test User API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123',
            role='customer'
        )
        self.supplier_user = User.objects.create_user(
            username='supplier',
            email='supplier@example.com',
            password='supplierpass123',
            role='supplier'
        )
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'customer'
        }
        response = self.client.post('/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.data['username'], 'newuser')
    
    def test_user_login(self):
        """Test user login endpoint"""
        data = {
            'username': 'customer',
            'password': 'customerpass123'
        }
        response = self.client.post('/users/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('username', response.data)
        self.assertIn('role', response.data)
    
    def test_user_list_as_admin(self):
        """Test admin can list all users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_user_list_as_customer(self):
        """Test customer cannot list users"""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/users/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access control"""
        # Admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        
        # Customer access denied
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/users/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AnalyticsTestCase(TestCase):
    """Test analytics functions"""
    
    def setUp(self):
        from orders.models import Order
        from products.models import Product, Category
        from users.models import User
        
        self.admin = User.objects.create_superuser(username='admin', password='admin123')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            category=self.category,
            price=1000,
            stock=10,
            supplier=self.supplier
        )
    
    def test_admin_dashboard_stats(self):
        """Test admin dashboard statistics"""
        from .analytics import get_admin_dashboard_stats
        
        stats = get_admin_dashboard_stats()
        self.assertIn('total_revenue', stats)
        self.assertIn('order_status_counts', stats)
        self.assertIn('sales_last_month', stats)
        self.assertIn('top_products', stats)
        self.assertIn('top_suppliers', stats)
        self.assertIn('low_stock_products', stats)