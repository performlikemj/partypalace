from django.urls import path
from . import views

urlpatterns = [
    path('', views.theme_list, name='theme_list'),   # /themes/
    path('<slug:slug>/', views.theme_detail, name='theme_detail'),
]
