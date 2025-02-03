from django.db import models
from colorfield.fields import ColorField
# Import your Theme model from themes app
from themes.models import Theme

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    background_color = ColorField(
        default='#F56C6C',
        help_text="Pick a background color for this circle."
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Many-to-many relationship to Theme
    themes = models.ManyToManyField(
        Theme,
        blank=True,              # optional
        related_name='products'  # lets us do theme.products.all()
    )
    
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    background_color = ColorField(
        default='#F56C6C',
        help_text="Pick a background color for this circle."
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # New field for “Popular Items”
    is_popular = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_popular:
            # Exclude the current product and order by creation (or some other field)
            popular_products = Product.objects.filter(is_popular=True).exclude(pk=self.pk).order_by('id')
            if popular_products.count() >= 5:
                # Unmark the oldest popular product
                oldest = popular_products.first()
                oldest.is_popular = False
                oldest.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name