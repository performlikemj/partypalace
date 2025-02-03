from django.contrib import admin
from .models import Theme

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured',)  # make is_featured editable in the admin list view
