from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .models import CartItem
from django.conf import settings

# Create your views here.

def cart_detail(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({
                'id': f"guest_{product_id}",
                'product': product,
                'quantity': quantity,
                'get_total_price': product.price * quantity
            })
    
    total = sum(item.get_total_price() if hasattr(item, 'get_total_price') 
                else item['get_total_price'] for item in cart_items)
    
    return render(request, 'cart/cart_detail.html', {
        'cart_items': cart_items,
        'total': total,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
    
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart:cart_detail')

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        product_id = item_id.replace('guest_', '')
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
    
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')

def update_cart(request, item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully.')
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart.')
        except ValueError:
            messages.error(request, 'Invalid quantity provided.')
    else:
        try:
            cart = request.session.get('cart', {})
            product_id = item_id.replace('guest_', '')
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[product_id] = quantity
            else:
                del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Cart updated successfully.')
        except ValueError:
            messages.error(request, 'Invalid quantity provided.')
    
    return redirect('cart:cart_detail')
