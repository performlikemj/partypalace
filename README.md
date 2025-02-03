# Party Supplies Store - Product Upload Guide

## Bulk Product Upload Instructions

### Prerequisites
- Admin access to the Django admin interface
- CSV file with product data
- ZIP file containing product images

### CSV File Format
Create a CSV file with the following structure:

```csv
name,slug,category,description,price,image_filename,background_color,themes,is_popular
"Birthday Balloons","birthday-balloons","Decorations","Colorful balloons",9.99,"balloons.jpg","#FF5733","birthday,party",true
```

#### Required Fields
- `name`: Product name
- `slug`: URL-friendly name (e.g., "birthday-balloons")
- `category`: Category name (will be created if doesn't exist)
- `description`: Product description
- `price`: Decimal number (e.g., 9.99)
- `image_filename`: Must match image file in ZIP

#### Optional Fields
- `background_color`: Hex color code (default: #F56C6C)
- `themes`: Comma-separated theme slugs (e.g., "birthday,party")
- `is_popular`: true/false (default: false)

### Image Requirements
1. Create a ZIP file containing all product images
2. Image filenames must match `image_filename` in CSV
3. Supported formats: JPG, PNG
4. Images will be stored in the `products/` directory

### Upload Steps
1. Log into Django Admin
2. Navigate to Products section
3. Click "Bulk Upload Products" button
4. Upload both CSV and ZIP files
5. Submit and wait for confirmation

### Important Notes
- Maximum 5 products can be marked as popular
- Themes must exist in the system before upload
- Categories are created automatically if they don't exist
- The system will validate:
  - Required fields
  - Image file existence
  - Theme existence
  - Popular item limit

### Example CSV Row
```csv
name,slug,category,description,price,image_filename,background_color,themes,is_popular
"Party Pack","party-pack","Party Sets","Complete party kit",29.99,"party-pack.jpg","#4287f5","birthday,celebration",true
```

### Error Handling
- Each row is processed independently
- Failed rows won't affect successful uploads
- Error messages will show:
  - Row identification
  - Error description
- Success/error count displayed after completion

For implementation details, see:

```26:110:partyproject/products/admin.py
@admin.register(Product)    
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_popular', 'background_color')
    list_editable = ('is_popular',)
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        ColorField: {'widget': ColorWidget},
    }
    filter_horizontal = ('themes',)
    change_list_template = "admin/products/product/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.bulk_upload_view, name='product-bulk-upload'),
        ]
        return custom_urls + urls
    def bulk_upload_view(self, request):
        if request.method == 'POST':
            form = ProductBulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                images_zip = zipfile.ZipFile(request.FILES['images_zip'])
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    images_zip.extractall(temp_dir)
                    
                    reader = csv.DictReader(csv_file)
                    success_count = 0
                    error_count = 0
                    
                    for row in reader:
                        try:
                            category, _ = Category.objects.get_or_create(
                                name=row['category'],
                                defaults={'slug': row['category'].lower().replace(' ', '-')}
                            )
                            
                            product = Product(
                                name=row['name'],
                                slug=row['slug'],
                                category=category,
                                description=row['description'],
                                price=row['price'],
                                background_color=row.get('background_color', '#F56C6C'),
                                is_popular=row.get('is_popular', '').lower() == 'true'
                            )
                            
                            image_filename = row.get('image_filename')
                            if image_filename:
                                image_path = os.path.join(temp_dir, image_filename)
                                if os.path.exists(image_path):
                                    with open(image_path, 'rb') as img_file:
                                        product.image.save(image_filename, File(img_file), save=False)
                            product.save()
                            
                            if 'themes' in row and row['themes']:
                                theme_slugs = [t.strip() for t in row['themes'].split(',')]
                                product.themes.set(Theme.objects.filter(slug__in=theme_slugs))
                            
                            success_count += 1
                            
                        except Exception as e:
                            error_count += 1
                            self.message_user(
                                request,
                                f"Error processing row {row.get('name', 'unknown')}: {str(e)}",
                                level=messages.ERROR
                            )

                    self.message_user(
                        request,
                        f"Bulk upload complete. {success_count} products created successfully. {error_count} errors.",
                        level=messages.SUCCESS if error_count == 0 else messages.WARNING
                    )
                    return redirect('admin:products_product_changelist')
            
        form = ProductBulkUploadForm()
        return render(
            request,
            'admin/products/product/bulk_upload.html',
            {'form': form}
        )
```


For the upload form template, see:

```1:23:partyproject/templates/admin/products/product/bulk_upload.html
{% extends "admin/base_site.html" %}
{% load i18n static %}

{% block content %}
<div>
    <h1>Bulk Upload Products</h1>
    
    <div class="module">
        <h2>Upload Instructions</h2>
        <ul>
            <li>Prepare a CSV file with the following columns: name, slug, category, description, price, image_filename, background_color (optional), themes (optional), is_popular (optional)</li>
            <li>Prepare a ZIP file containing all product images</li>
            <li>The image_filename in the CSV should match exactly with the filename in the ZIP</li>
        </ul>
    </div>

    <form action="." method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <input type="submit" value="Upload" class="default" style="float: none">
    </form>
</div>
{% endblock %} 
```

