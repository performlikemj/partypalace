from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
from ..models import Product, Category
from themes.models import Theme
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheets_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            FIXED_PORT = 63244  # or any port you choose
            creds = flow.run_local_server(port=FIXED_PORT)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)

def sync_products_from_sheet(spreadsheet_id, range_name):
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return 'No data found.'

    headers = [h.strip().lower() for h in values[0]]
    for row in values[1:]:
        data = dict(zip(headers, row))
        print(f"Processing product: {data.get('name')}")
        
        # Generate SKU
        category_name = data['category'].upper().replace(' ', '_')
        theme_name = data.get('theme', 'NO_THEME').upper().replace(' ', '_')
        product_name = data['name'].upper().replace(' ', '_')
        sku = f"{category_name}_{theme_name}_{product_name}"
        
        # Create category
        category, _ = Category.objects.get_or_create(
            name=data['category'],
            defaults={'slug': data['category'].lower().replace(' ', '-')}
        )

        try:
            # Try to get existing product by SKU
            product = Product.objects.filter(sku=sku).first()
            
            # Prepare product data
            product_data = {
                'name': data['name'],
                'slug': data['slug'],
                'category': category,
                'description': data['description'],
                'price': data['price'],
                'background_color': data.get('background color', '#F56C6C'),
                'is_popular': data.get('is popular', '').lower() == 'true'
            }

            if product:
                # Update existing product
                for key, value in product_data.items():
                    setattr(product, key, value)
                product.save()
                print(f"Updated existing product: {product.name}")
            else:
                # Create new product with SKU
                product_data['sku'] = sku
                product = Product.objects.create(**product_data)
                print(f"Created new product: {product.name}")

            # Handle themes
            if 'theme' in data:
                theme_slug = data['theme'].lower().replace(' ', '-')
                theme, _ = Theme.objects.get_or_create(
                    slug=theme_slug,
                    defaults={'name': data['theme']}
                )
                product.themes.set([theme])

        except Exception as e:
            print(f"Error processing product {data.get('name')}: {str(e)}")
            continue

    return 'Sync completed successfully.' 