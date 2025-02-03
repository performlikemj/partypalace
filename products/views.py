from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/categories.html', {'categories': categories})

def product_list(request, category_slug=None):
    category = None
    products = Product.objects.all().order_by('name')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Paginate all results (filtered or not)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_slug):
    # Fetch a single product by its slug
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'products/product_detail.html', {'product': product})