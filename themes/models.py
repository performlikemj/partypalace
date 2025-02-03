from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='themes/', blank=True, null=True)

    # New field for marking a single featured theme
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If this theme is being set to featured,
        # un-feature any other theme.
        if self.is_featured:
            # Update all other themes, set them to not featured
            Theme.objects.filter(is_featured=True).exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name