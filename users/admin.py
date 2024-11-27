from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ServiceItem, Cart, Order, OrderItem
from users.models import ServiceItem

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)  

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'date_ordered')
    inlines = [OrderItemInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ServiceItem)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
