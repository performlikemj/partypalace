from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_review, name='submit_review'),
    path('submit/<int:product_id>/', views.submit_review, name='submit_product_review'),
]