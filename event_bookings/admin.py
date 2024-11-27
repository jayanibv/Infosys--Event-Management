from django.contrib import admin
from .models import Hall,Booking  # Import your Hall model

# Register the Hall model with the admin site
admin.site.register(Hall)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('hall', 'event_name', 'booking_date', 'start_time', 'end_time')
    list_filter = ('hall', 'booking_date')
    search_fields = ('event_name', 'hall__name')