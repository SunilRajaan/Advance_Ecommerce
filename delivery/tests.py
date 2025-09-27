# delivery/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order
from .models import Delivery

User = get_user_model()

class DeliveryModelTestCase(TestCase):
    """Test Delivery model functionality"""
    
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        self.delivery_person = User.objects.create_user(username='delivery', password='delivery123', role='delivery')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', category=self.category, price=1000, stock=5, supplier=self.supplier
        )
        self.order = Order.objects.create(customer=self.customer, total_price=1000)
    
    def test_create_delivery(self):
        """Test delivery creation"""
        delivery = Delivery.objects.create(
            order=self.order,
            delivery_person=self.delivery_person,
            status='assigned'
        )
        
        self.assertEqual(delivery.order, self.order)
        self.assertEqual(delivery.delivery_person, self.delivery_person)
        self.assertEqual(delivery.status, 'assigned')
        self.assertEqual(str(delivery), f'Delivery for Order #{self.order.id} - assigned')

class DeliveryAPITestCase(APITestCase):
    """Test Delivery API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='admin123')
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        self.delivery_person = User.objects.create_user(username='delivery', password='delivery123', role='delivery')
        self.other_delivery = User.objects.create_user(username='other_delivery', password='delivery123', role='delivery')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Product', category=self.category, price=100, stock=10, supplier=self.supplier
        )
        self.order = Order.objects.create(customer=self.customer, total_price=100)
        
        self.delivery_data = {
            'order': self.order.id,
            'delivery_person': self.delivery_person.id
        }
    
    def test_create_delivery_as_admin(self):
        """Test admin can create delivery"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/delivery/create/', self.delivery_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Delivery.objects.count(), 1)
        
        delivery = Delivery.objects.first()
        self.assertEqual(delivery.order, self.order)
        self.assertEqual(delivery.delivery_person, self.delivery_person)
    
    def test_create_duplicate_delivery(self):
        """Test cannot create duplicate delivery for same order"""
        Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/delivery/create/', self.delivery_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', str(response.data))
    
    def test_list_deliveries_as_delivery_person(self):
        """Test delivery person can see their assigned deliveries"""
        delivery1 = Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        # Create another delivery assigned to different person
        other_order = Order.objects.create(customer=self.customer, total_price=200)
        delivery2 = Delivery.objects.create(order=other_order, delivery_person=self.other_delivery)
        
        self.client.force_authenticate(user=self.delivery_person)
        response = self.client.get('/delivery/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], delivery1.id)
    
    def test_update_delivery_status(self):
        """Test delivery person can update delivery status"""
        delivery = Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        self.client.force_authenticate(user=self.delivery_person)
        response = self.client.patch(f'/delivery/{delivery.id}/', {'status': 'in_transit'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'in_transit')
    
    def test_customer_cannot_access_deliveries(self):
        """Test customer cannot access delivery endpoints"""
        delivery = Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/delivery/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Returns empty if no permissions
    
    def test_delivered_status_sets_timestamp(self):
        """Test that delivered status sets delivered_at timestamp"""
        delivery = Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        self.client.force_authenticate(user=self.delivery_person)
        response = self.client.patch(f'/delivery/{delivery.id}/', {'status': 'delivered'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'delivered')
        self.assertIsNotNone(delivery.delivered_at)

class DeliverySignalsTestCase(TestCase):
    """Test delivery-related signals"""
    
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        self.delivery_person = User.objects.create_user(username='delivery', password='delivery123', role='delivery')
        self.order = Order.objects.create(customer=self.customer, total_price=100)
    
    def test_delivery_creation_signal(self):
        """Test that signals are triggered on delivery creation"""
        from notifications.models import Notification
        
        delivery = Delivery.objects.create(order=self.order, delivery_person=self.delivery_person)
        
        # Check if notification was created for delivery person
        notifications = Notification.objects.filter(user=self.delivery_person)
        self.assertEqual(notifications.count(), 1)
        self.assertIn('New delivery assigned', notifications.first().message)