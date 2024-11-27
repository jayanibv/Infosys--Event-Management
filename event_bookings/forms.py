# event_bookings/forms.py
from django import forms
from .models import Hall

class HallUpdateForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['name', 'location', 'capacity']
