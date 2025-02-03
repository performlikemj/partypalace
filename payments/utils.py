import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_session(order):
    line_items = []
    
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.product.price * 100),
                'product_data': {
                    'name': item.product.name,
                    'description': item.product.description,
                    'images': [item.product.image.url] if item.product.image else [],
                },
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=settings.SITE_URL + '/payments/order/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=settings.SITE_URL + '/cart/',
        metadata={
            'order_id': order.id
        }
    )
    
    return session 