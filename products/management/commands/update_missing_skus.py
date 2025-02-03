from django.core.management.base import BaseCommand
from products.models import Product
from django.db.models import Q

class Command(BaseCommand):
    help = 'Updates products missing SKU values'

    def handle(self, *args, **options):
        # Look for products where sku is either null, an empty string, or "1"
        products = Product.objects.filter(Q(sku__isnull=True) | Q(sku='') | Q(sku='1'))
        count = 0
        for product in products:
            generated_sku = f"{product.category.name}_{product.name}".upper().replace(" ", "_")
            product.sku = generated_sku
            product.save()
            count += 1
            self.stdout.write(f"Updated Product {product.id} with SKU {generated_sku}")
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} products"))