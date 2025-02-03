from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Order, User
import stripe
from .utils import create_stripe_session
from django.core.mail import send_mail
from cart.models import CartItem
from products.models import Product
from django.contrib import messages
from django.contrib.sessions.models import Session
from accounts.models import OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # Get cart items and total
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
                total = sum(item.get_total_price() for item in cart_items)
            else:
                cart = request.session.get('cart', {})
                cart_items = []
                total = 0
                for product_id, quantity in cart.items():
                    product = Product.objects.get(id=product_id)
                    total += product.price * quantity
                    cart_items.append({
                        'product': product,
                        'quantity': quantity
                    })

            if not cart_items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            # Create Stripe session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Cart Total',
                        },
                        'unit_amount': int(total * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/cart/'),
                metadata={
                    'user_id': str(request.user.id) if request.user.is_authenticated else 'guest',
                    'cart_session': request.session.session_key
                }
            )

            return JsonResponse({'sessionId': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle different event types
    try:
        if event['type'] == 'checkout.session.completed':
            handle_checkout_session_completed(event)
        elif event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event)
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_intent_failed(event)
        elif event['type'] == 'charge.refunded':
            handle_charge_refunded(event)
        
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)

def handle_checkout_session_completed(event):
    session = event['data']['object']
    user_id = session['metadata'].get('user_id')
    cart_session = session['metadata'].get('cart_session')
    
    try:
        # Create order
        if user_id != 'guest':
            user = User.objects.get(id=user_id)
            order = Order.objects.create(
                user=user,
                total_amount=session['amount_total'] / 100,
                stripe_payment_intent=session['payment_intent'],
                status='processing',
                payment_status='paid',
                email=user.email
            )
            # Create OrderItems from user's cart
            cart_items = CartItem.objects.filter(user=user)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            # Clear authenticated user's cart
            cart_items.delete()
        else:
            order = Order.objects.create(
                session_key=cart_session,
                total_amount=session['amount_total'] / 100,
                stripe_payment_intent=session['payment_intent'],
                status='processing',
                payment_status='paid'
            )
            # Create OrderItems from session cart
            if cart_session:
                try:
                    session_obj = Session.objects.get(session_key=cart_session)
                    session_data = session_obj.get_decoded()
                    cart = session_data.get('cart', {})
                    for product_id, quantity in cart.items():
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                except Session.DoesNotExist:
                    pass

        # Send confirmation email
        send_order_confirmation_email(order)
        return True
    except Exception as e:
        return False

def handle_payment_intent_succeeded(event):
    payment_intent = event['data']['object']
    order = Order.objects.get(stripe_payment_intent=payment_intent.id)
    order.status = 'processing'
    order.save()

def handle_payment_intent_failed(event):
    payment_intent = event['data']['object']
    order = Order.objects.get(stripe_payment_intent=payment_intent.id)
    order.status = 'cancelled'
    order.save()

    # Notify customer of failed payment
    send_payment_failed_email(order)

def handle_charge_refunded(event):
    charge = event['data']['object']
    order = Order.objects.get(payment_id=charge.payment_intent)
    order.status = 'refunded'
    order.save()

    # Send refund confirmation
    send_refund_confirmation_email(order)

# Helper functions for email notifications
def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    message = f'''
    Thank you for your order!
    
    Order Details:
    Order Number: {order.id}
    Total Amount: ${order.total_amount}
    Status: {order.get_status_display()}
    
    We'll notify you when your order ships.
    '''
    
    # Get the email address based on whether it's a guest or authenticated user
    if hasattr(order, 'user') and order.user:
        email = order.user.email
    else:
        # For guest orders, use the email stored in the order
        email = order.email
    
    if email:  # Only send if we have an email address
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

def send_payment_failed_email(order):
    subject = f'Payment Failed - Order #{order.id}'
    message = f'''
    We were unable to process your payment for Order #{order.id}.
    
    Order Details:
    Order Number: {order.id}
    Total Amount: ${order.total_amount}
    Status: {order.get_status_display()}
    
    Please try again or contact our support team if you need assistance.
    '''
    
    if hasattr(order, 'user') and order.user:
        email = order.user.email
    else:
        email = order.email
    
    if email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

def send_refund_confirmation_email(order):
    subject = f'Refund Confirmation - Order #{order.id}'
    message = f'''
    Your refund has been processed for Order #{order.id}.
    
    Refund Details:
    Order Number: {order.id}
    Refund Amount: ${order.total_amount}
    Status: {order.get_status_display()}
    
    The refund should appear on your statement within 5-10 business days.
    If you have any questions, please contact our support team.
    '''
    
    if hasattr(order, 'user') and order.user:
        email = order.user.email
    else:
        email = order.email
    
    if email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

def order_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.warning(request, 'No order session found.')
        return redirect('home')
        
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Create or get order based on session data
        if session.metadata.get('user_id') != 'guest':
            try:
                order = Order.objects.get(stripe_payment_intent=session.payment_intent)
            except Order.DoesNotExist:
                messages.warning(request, 'Order not found. Please contact support.')
                return redirect('home')
        else:
            try:
                order = Order.objects.get(session_key=session.metadata.get('cart_session'))
            except Order.DoesNotExist:
                messages.warning(request, 'Guest order not found. Please contact support.')
                return redirect('home')
            
        # Clear the cart
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user).delete()
        else:
            request.session['cart'] = {}
            request.session.modified = True
            
        return render(request, 'payments/success.html', {'order': order})
        
    except stripe.error.StripeError as e:
        messages.error(request, 'There was an error processing your payment. Please contact support.')
        return redirect('home')
    except Exception as e:
        messages.error(request, 'An unexpected error occurred. Please contact support.')
        return redirect('home')

def cart_detail(request):
    context = {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    # Add existing context
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
    
    context.update({
        'cart_items': cart_items,
        'total': total
    })
    
    return render(request, 'cart/cart_detail.html', context) 