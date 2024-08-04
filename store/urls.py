from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import sign_in, Index, login, logout, cart, add_to_cart, remove_from_cart,  update_cart, add_order, orders, single_product

urlpatterns = [
    path('', Index, name='home'),
    path('signup/', sign_in, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    # path('product/',products,name='products'),
    path('add_to_cart/<int:product_id>', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>',
         remove_from_cart, name='remove_from_cart'),
    path('update_cart', update_cart, name='update_cart'),
    path('cart/', cart, name='cart'),
    path('place_order/', add_order, name='place_order'),
    path('orders/', orders, name='orders'),
    path('single_product/<int:product_id>',
         single_product, name='single_product'),

]
