import tempfile
from django.contrib import admin
from colorfield.fields import ColorField
from colorfield.widgets import ColorWidget
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import Product, Category
from themes.models import Theme
from .forms import ProductBulkUploadForm
import csv
import zipfile
from io import TextIOWrapper
from django.core.files import File
from django.conf import settings
import os

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'background_color')
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        ColorField: {'widget': ColorWidget},
    }

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