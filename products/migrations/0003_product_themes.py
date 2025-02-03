# Generated by Django 5.1.5 on 2025-01-22 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_category_background_color_product_background_color'),
        ('themes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='themes',
            field=models.ManyToManyField(blank=True, related_name='products', to='themes.theme'),
        ),
    ]
