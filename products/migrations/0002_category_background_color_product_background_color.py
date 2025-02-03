# Generated by Django 5.1.5 on 2025-01-22 05:53

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_color',
            field=colorfield.fields.ColorField(default='#F56C6C', help_text='Pick a background color for this circle.', image_field=None, max_length=25, samples=None),
        ),
        migrations.AddField(
            model_name='product',
            name='background_color',
            field=colorfield.fields.ColorField(default='#F56C6C', help_text='Pick a background color for this circle.', image_field=None, max_length=25, samples=None),
        ),
    ]
