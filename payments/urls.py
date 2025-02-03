from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('success/', views.order_success, name='success'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
] 