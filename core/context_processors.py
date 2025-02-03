# core/context_processors.py (example location)

from products.models import Category
from themes.models import Theme
from .models import AboutPage, ContactPage

def nav_categories_and_themes(request):
    """Returns a list of all Categories and Themes for the global nav dropdown."""
    return {
        'nav_categories': Category.objects.all(),
        'nav_themes': Theme.objects.all(),
    }

def footer_content(request):
    return {
        'about_footer': AboutPage.objects.first(),
        'contact_footer': ContactPage.objects.first(),
    }