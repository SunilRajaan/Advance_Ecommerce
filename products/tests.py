from django.test import TestCase
from .models import Product, Category
from users.models import User

class ProductTestCase(TestCase):
    def setUp(self):
        supplier = User.objects.create_user(username='supplier1', password='pass', role='supplier')
        category = Category.objects.create(name='Electronics')
        Product.objects.create(name='Laptop', category=category, price=1000, stock=10, supplier=supplier)

    def test_product_creation(self):
        product = Product.objects.get(name='Laptop')
        self.assertEqual(product.stock, 10)