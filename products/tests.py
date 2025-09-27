# products/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category

User = get_user_model()

class ProductModelTestCase(TestCase):
    """Test Product model functionality"""
    
    def setUp(self):
        self.supplier = User.objects.create_user(
            username='supplier',
            password='supplier123',
            role='supplier'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )
    
    def test_create_product(self):
        """Test product creation"""
        product = Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            category=self.category,
            price=699.99,
            stock=50,
            supplier=self.supplier
        )
        self.assertEqual(product.name, 'Smartphone')
        self.assertEqual(product.category.name, 'Electronics')
        self.assertEqual(product.supplier.username, 'supplier')
        self.assertEqual(product.stock, 50)
    
    def test_product_string_representation(self):
        """Test product string representation"""
        product = Product.objects.create(
            name='Tablet',
            category=self.category,
            price=299.99,
            stock=25,
            supplier=self.supplier
        )
        self.assertEqual(str(product), 'Tablet (Electronics)')
    
    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(
            name='Books',
            description='Various books'
        )
        self.assertEqual(category.name, 'Books')
        self.assertEqual(str(category), 'Books')

class ProductAPITestCase(APITestCase):
    """Test Product API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='admin123')
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        self.customer = User.objects.create_user(username='customer', password='customer123', role='customer')
        
        self.category = Category.objects.create(name='Electronics')
        self.product_data = {
            'name': 'Laptop',
            'description': 'Gaming laptop',
            'category_id': self.category.id,
            'price': 1299.99,
            'stock': 15
        }
    
    def test_create_product_as_supplier(self):
        """Test supplier can create product"""
        self.client.force_authenticate(user=self.supplier)
        response = self.client.post('/products/', self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().supplier, self.supplier)
    
    def test_create_product_as_customer(self):
        """Test customer cannot create product"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/products/', self.product_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_products(self):
        """Test product listing with filtering"""
        # Create test products
        product1 = Product.objects.create(
            name='Product 1', category=self.category, price=100, stock=10, supplier=self.supplier
        )
        product2 = Product.objects.create(
            name='Product 2', category=self.category, price=200, stock=0, supplier=self.supplier
        )
        
        # Customer sees only products with stock > 0
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Supplier sees all their products
        self.client.force_authenticate(user=self.supplier)
        response = self.client.get('/products/')
        self.assertEqual(len(response.data['results']), 2)
    
    def test_product_search(self):
        """Test product search functionality"""
        Product.objects.create(
            name='iPhone', category=self.category, price=999, stock=5, supplier=self.supplier
        )
        Product.objects.create(
            name='Samsung Phone', category=self.category, price=899, stock=3, supplier=self.supplier
        )
        
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/products/?search=iPhone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'iPhone')
    
    def test_supplier_dashboard_access(self):
        """Test supplier dashboard access"""
        self.client.force_authenticate(user=self.supplier)
        response = self.client.get('/products/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_products', response.data)
        self.assertIn('low_stock', response.data)
        
        # Customer cannot access supplier dashboard
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/products/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ProductUtilsTestCase(TestCase):
    """Test product utility functions"""
    
    def setUp(self):
        self.supplier = User.objects.create_user(username='supplier', password='supplier123', role='supplier')
        self.category = Category.objects.create(name='Electronics')
        
        # Create low stock products
        self.low_stock_product = Product.objects.create(
            name='Low Stock Item', category=self.category, price=100, stock=3, supplier=self.supplier
        )
    
    def test_low_stock_notification(self):
        """Test low stock notification utility"""
        from .utils import batch_notify_low_stock
        from django.core import mail
        
        # Mock email sending and test the function
        batch_notify_low_stock()
        
        # In a real test, you'd check if emails were queued/sent
        # This tests that the function runs without errors
        self.assertTrue(True)  # Placeholder assertion