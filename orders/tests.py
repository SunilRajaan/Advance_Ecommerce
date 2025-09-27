# orders/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from .models import Order, OrderItem

User = get_user_model()

class OrderModelTestCase(TestCase):
    """Test Order model functionality"""
    
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer', password='customer123', role='customer'
        )
        self.supplier = User.objects.create_user(
            username='supplier', password='supplier123', role='supplier'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', category=self.category, price=1000, stock=10, supplier=self.supplier
        )
    
    def test_create_order(self):
        """Test order creation"""
        order = Order.objects.create(customer=self.customer, total_price=1000)
        order_item = OrderItem.objects.create(
            order=order, product=self.product, quantity=1, price=1000
        )
        
        self.assertEqual(order.customer.username, 'customer')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(str(order), f'Order #{order.id} (pending)')
        self.assertEqual(str(order_item), 'Laptop x 1')

class OrderAPITestCase(APITestCase):
    """Test Order API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='admin123')
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        self.delivery_person = User.objects.create_user(username='delivery', password='delivery123', role='delivery')
        
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Product 1', category=self.category, price=100, stock=5, supplier=self.supplier
        )
        self.product2 = Product.objects.create(
            name='Product 2', category=self.category, price=200, stock=3, supplier=self.supplier
        )
        
        self.order_data = {
            'items': [
                {'product': self.product1.id, 'quantity': 2},
                {'product': self.product2.id, 'quantity': 1}
            ]
        }
    
    def test_create_order_as_customer(self):
        """Test customer can create order"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/orders/', self.order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_price, 400)  # (2*100) + (1*200)
        
        # Check stock was reduced
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 3)  # 5-2=3
        self.assertEqual(self.product2.stock, 2)  # 3-1=2
    
    def test_create_order_insufficient_stock(self):
        """Test order creation fails with insufficient stock"""
        self.client.force_authenticate(user=self.customer)
        invalid_order_data = {
            'items': [{'product': self.product1.id, 'quantity': 10}]  # Only 5 in stock
        }
        
        response = self.client.post('/orders/', invalid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', str(response.data))
    
    def test_list_orders_as_customer(self):
        """Test customer can only see their own orders"""
        # Create orders for different customers
        other_customer = User.objects.create_user(username='other', password='other123', role='customer')
        order1 = Order.objects.create(customer=self.customer, total_price=100)
        order2 = Order.objects.create(customer=other_customer, total_price=200)
        
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], order1.id)
    
    def test_list_orders_as_admin(self):
        """Test admin can see all orders"""
        order1 = Order.objects.create(customer=self.customer, total_price=100)
        order2 = Order.objects.create(customer=self.supplier, total_price=200)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_order_status(self):
        """Test order status update permissions"""
        order = Order.objects.create(customer=self.customer, total_price=100)
        
        # Delivery person can update status
        self.client.force_authenticate(user=self.delivery_person)
        response = self.client.patch(f'/orders/{order.id}/', {'status': 'confirmed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Customer cannot update status (except maybe to cancel)
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f'/orders/{order.id}/', {'status': 'shipped'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrderSignalsTestCase(TestCase):
    """Test order-related signals"""
    
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product', category=self.category, price=100, stock=10, supplier=self.supplier
        )
    
    def test_order_creation_signal(self):
        """Test that signals are triggered on order creation"""
        from notifications.models import Notification
        
        order = Order.objects.create(customer=self.customer, total_price=100)
        
        # Check if notification was created
        notifications = Notification.objects.filter(user=self.customer)
        self.assertEqual(notifications.count(), 1)
        self.assertIn('has been placed', notifications.first().message)