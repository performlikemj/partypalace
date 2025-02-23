# Generated by Django 5.1.5 on 2025-01-25 14:55

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('mission_statement', models.TextField()),
                ('vision', models.TextField()),
                ('history', models.TextField()),
                ('team_section_title', models.CharField(default='Our Team', max_length=200)),
                ('accent_color', colorfield.fields.ColorField(default='#4A90E2', image_field=None, max_length=25, samples=None)),
            ],
            options={
                'verbose_name_plural': 'About Page',
            },
        ),
        migrations.CreateModel(
            name='ContactPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.TextField()),
                ('address', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('business_hours', models.TextField()),
                ('map_embed_code', models.TextField(blank=True)),
                ('facebook', models.URLField(blank=True)),
                ('instagram', models.URLField(blank=True)),
                ('twitter', models.URLField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Contact Page',
            },
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=200)),
                ('answer', models.TextField()),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQs',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('bio', models.TextField()),
                ('image', models.ImageField(upload_to='team/')),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
