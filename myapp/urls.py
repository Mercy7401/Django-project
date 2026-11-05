
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('bag/', views.cart, name='cart'),
    path('bag/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('bag/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<uuid:reference>/', views.order_success, name='order_success'),
]
