from django.core.management.base import BaseCommand
from products.utils.sheets_sync import sync_products_from_sheet
from django.conf import settings

class Command(BaseCommand):
    help = 'Sync products from Google Sheets'

    def handle(self, *args, **options):
        spreadsheet_id = settings.GOOGLE_SHEETS_PRODUCT_ID
        range_name = 'Products!A1:I'  # Adjust range as needed
        result = sync_products_from_sheet(spreadsheet_id, range_name)
        self.stdout.write(self.style.SUCCESS(result)) 