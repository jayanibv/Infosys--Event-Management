from django.urls import path
from . import views

app_name = 'bookings' 

urlpatterns = [
    path('check_availability/', views.check_availability, name='check_availability'),
    path('bookings/book/<int:hall_id>/', views.book_hall, name='book_hall'),
    path('update/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('update_details/<int:booking_id>/', views.update_details, name='update_booking_details'),
    path('halls/update/<int:hall_id>/', views.update_hall_details, name='update_hall_details'),
    path('bookings/', views.bookings, name='bookings'),
    path('bookings/confirm_order/<int:booking_id>/', views.confirm_order, name='confirm_order'),
    path('book/<int:booking_id>/payment/', views.payment_page, name='payment_page'),
    path('bookings/order_confirmation/<int:booking_id>/', views.order_confirmation, name='order_confirmation'),
    path('bookings/payment_failure/<int:booking_id>/', views.payment_failure, name='payment_failure'),
]
