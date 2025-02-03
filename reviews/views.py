from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from products.models import Product
from accounts.models import Order

@login_required
def submit_review(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user has purchased the product
        has_purchased = Order.objects.filter(
            user=request.user,
            status='delivered',
            items__product=product
        ).exists()
        
        if not has_purchased:
            messages.error(request, "You can only review products you have purchased and received.")
            return redirect('product_detail', product_slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            if product:
                review.product = product
            review.save()
            messages.success(request, "Thanks! Your review is pending approval.")
            return redirect('product_detail', product_slug=review.product.slug)
    else:
        initial = {'product': product} if product else {}
        form = ReviewForm(initial=initial)

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'reviews/submit_review.html', context)