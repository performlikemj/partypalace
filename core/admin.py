from django.contrib import admin
from django.utils.html import format_html
from .models import AboutPage, TeamMember, ContactPage, FAQ, ShippingPolicy, ReturnPolicy

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview_image')
    fieldsets = (
        ('Page Header', {
            'fields': ('title', 'main_image', 'mission_statement')
        }),
        ('Content Sections', {
            'fields': ('vision', 'history', 'team_section_title')
        }),
        ('Styling', {
            'fields': ('accent_color',),
            'classes': ('collapse',)
        })
    )

    def preview_image(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.main_image.url)
        return "No image"
    preview_image.short_description = 'Main Image'

    def has_add_permission(self, request):
        # Check if an AboutPage already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'preview_image', 'order')
    list_editable = ('order',)
    ordering = ('order',)
    search_fields = ('name', 'position')

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 25px;"/>', obj.image.url)
        return "No image"
    preview_image.short_description = 'Photo'

@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'email', 'phone')
    fieldsets = (
        ('Page Header', {
            'fields': ('title', 'subtitle')
        }),
        ('Contact Information', {
            'fields': ('address', 'email', 'phone', 'business_hours')
        }),
        ('Map', {
            'fields': ('map_embed_code',),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'twitter'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        # Check if a ContactPage already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    list_editable = ('order',)
    ordering = ('order',)
    search_fields = ('question', 'answer')

    class Media:
        css = {
            'all': ('css/admin/faq.css',)
        }

@admin.register(ShippingPolicy)
class ShippingPolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated')
    search_fields = ('title', 'content')

@admin.register(ReturnPolicy)
class ReturnPolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated')
    search_fields = ('title', 'content')
