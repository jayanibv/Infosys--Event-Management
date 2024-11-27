from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

from .views import (
    register_view, login_view, logout_view, home_view, 
    services_view, cart_view, add_to_cart, flower_view, 
    catering_view, update_cart, remove_from_cart, checkout, place_order, order_confirmation
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('services/', services_view, name='services'),
    path('add_to_cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('flower-decoration/', flower_view, name='flower_decoration'),
    path('catering/', catering_view, name='catering'),
    path('update_cart/<int:cart_item_id>/', update_cart, name='update_cart'),
    path('remove_from_cart/<int:cart_item_id>/',remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('place_order/',place_order, name='place_order'),
    path('cart/payment/', views.cart_payment_page, name='cart_payment_page'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
