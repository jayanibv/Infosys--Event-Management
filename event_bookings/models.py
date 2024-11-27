from django.db import models
from django.utils import timezone
class Hall(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=50)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # New field for price

    def __str__(self):
        return f"{self.name} - {self.location} - Capacity: {self.capacity}"

class Booking(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    booking_date = models.DateField(default=timezone.now)
    end_date= models.DateField(default=timezone.now)
    date=models.DateField(default=timezone.now)
    payment_status = models.CharField(max_length=20, default="Pending")  # New Field
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=50, blank=True, default="Not Selected")


    def __str__(self):
        return f"Booking for {self.hall.name} on {self.booking_date}"