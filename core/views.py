from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from products.models import Category, Product
from themes.models import Theme
from reviews.models import Review
from django.core.mail import send_mail
from django.contrib import messages
from .models import AboutPage, ContactPage, TeamMember, FAQ, ShippingPolicy, ReturnPolicy
from django.core.paginator import Paginator


def home(request):
    # Show the first 6 categories in "Shop by Category" circles
    categories = Category.objects.order_by('name')[:6]

    # Show the first 6 themes in "Popular Themes"
    themes = Theme.objects.order_by('name')[:6]

    # Find the featured theme if it exists
    featured_theme = Theme.objects.filter(is_featured=True).first()

    popular_products = Product.objects.filter(is_popular=True)[:5]

    reviews_list = Review.objects.filter(
        is_approved=True
    ).select_related('user', 'product').order_by('-created_at')
    
    # Create paginator - 6 reviews per page
    paginator = Paginator(reviews_list, 6)
    page = request.GET.get('page')
    approved_reviews = paginator.get_page(page)
    

    # Group products by category for a "Products by Category" section
    categories_with_products = []
    all_categories = Category.objects.all()
    for cat in all_categories:
        prods = Product.objects.filter(category=cat)[:4]
        if prods.exists():
            categories_with_products.append({
                'category': cat,
                'products': prods
            })

    context = {
        'approved_reviews': approved_reviews,
        'categories': categories,
        'themes': themes,
        'featured_theme': featured_theme,
        'categories_with_products': categories_with_products,
        'popular_products': popular_products,
    }
    return render(request, 'core/home.html', context)

def search_view(request):
    query = request.GET.get('q', '').strip()  # get search term
    product_results = []
    category_results = []
    theme_results = []

    if query:
        # Filter products by name or description
        product_results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        # Filter categories by name
        category_results = Category.objects.filter(
            Q(name__icontains=query)
        )

        # Filter themes by name or description
        theme_results = Theme.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'query': query,
        'product_results': product_results,
        'category_results': category_results,
        'theme_results': theme_results,
    }
    return render(request, 'core/search_results.html', context)

def about(request):
    about_content = AboutPage.objects.first()
    team_members = TeamMember.objects.all()
    faqs = FAQ.objects.all()
    
    context = {
        'about': about_content,
        'team_members': team_members,
        'faqs': faqs,
    }
    return render(request, 'core/about.html', context)

def contact(request):
    contact_content = ContactPage.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email
        email_message = f"From: {name}\nEmail: {email}\n\n{message}"
        try:
            send_mail(
                subject,
                email_message,
                email,
                [contact_content.email],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again.')
        
    return render(request, 'core/contact.html', {'contact': contact_content})

def faq(request):
    faqs = FAQ.objects.all()
    return render(request, 'core/faq.html', {'faqs': faqs})

def shipping_policy(request):
    policy = get_object_or_404(ShippingPolicy)
    return render(request, 'core/shipping.html', {'policy': policy})

def return_policy(request):
    policy = get_object_or_404(ReturnPolicy)
    return render(request, 'core/returns.html', {'policy': policy})
