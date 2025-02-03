from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem, UserProfile
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Register OrderItem model
admin.site.register(OrderItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'total_amount', 'status', 'payment_status', 'created_at', 'stripe_link')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'email')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_intent', 'total_amount')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'email', 'total_amount', 'status', 'payment_status')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address',)
        }),
        ('Payment Information', {
            'fields': ('stripe_payment_intent', 'created_at', 'updated_at')
        }),
    )

    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return f"Guest ({obj.email})"
    
    def stripe_link(self, obj):
        if obj.stripe_payment_intent:
            url = f"https://dashboard.stripe.com/payments/{obj.stripe_payment_intent}"
            return format_html('<a href="{}" target="_blank">View in Stripe</a>', url)
        return "-"
    
    stripe_link.short_description = 'Stripe Payment'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # If status changed to 'refunded', process refund in Stripe
            if obj.status == 'refunded' and obj.stripe_payment_intent:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(obj.stripe_payment_intent)
                    if payment_intent.status == 'succeeded':
                        refund = stripe.Refund.create(
                            payment_intent=obj.stripe_payment_intent,
                            amount=int(obj.total_amount * 100)  # Convert to cents
                        )
                        obj.payment_status = 'refunded'
                except stripe.error.StripeError as e:
                    # Handle the error appropriately
                    pass
        
        super().save_model(request, obj, form, change)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country')
    search_fields = ('user__username', 'user__email', 'phone') 