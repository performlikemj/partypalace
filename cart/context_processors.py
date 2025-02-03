from .models import CartItem, Product

def cart_processor(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.get_total_price() for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        cart_count = sum(quantity for quantity in cart.values())
        cart_total = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_total += product.price * quantity
            except Product.DoesNotExist:
                continue

    return {
        'cart_count': cart_count,
        'cart_total': cart_total
    } 