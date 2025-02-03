from django.db import models
from colorfield.fields import ColorField

# Create your models here.

class AboutPage(models.Model):
    title = models.CharField(max_length=200)
    main_image = models.ImageField(upload_to='about/', blank=True, null=True)
    mission_statement = models.TextField()
    vision = models.TextField()
    history = models.TextField()
    team_section_title = models.CharField(max_length=200, default="Our Team")
    
    # Styling options
    accent_color = ColorField(default='#4A90E2')
    
    class Meta:
        verbose_name_plural = "About Page"
    
    def __str__(self):
        return "About Page Content"

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name

class ContactPage(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    business_hours = models.TextField()
    map_embed_code = models.TextField(blank=True)
    
    # Social Media Links
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    class Meta:
        verbose_name_plural = "Contact Page"
    
    def __str__(self):
        return "Contact Page Content"

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question

class ShippingPolicy(models.Model):
    title = models.CharField(max_length=200, default="Shipping Policy")
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Shipping Policy"

    def __str__(self):
        return self.title

class ReturnPolicy(models.Model):
    title = models.CharField(max_length=200, default="Returns/Refunds")
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Return Policy"

    def __str__(self):
        return self.title
