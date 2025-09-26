from django.core.management.base import BaseCommand
from products.utils import batch_notify_low_stock

class Command(BaseCommand):
    help = 'Checks for low stock and notifies suppliers via email'

    def handle(self, *args, **options):
        batch_notify_low_stock()
        self.stdout.write(self.style.SUCCESS('Successfully checked low stock and sent notifications'))