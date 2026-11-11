from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

from django import forms
from django.utils import timezone


class ReservationForm(forms.Form):
    booking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def clean(self):
        data = super().clean()
        start, end = data.get('booking_date'), data.get('return_date')
        if start and start < timezone.localdate():
            self.add_error('booking_date', 'Choose today or a future date.')
        if start and end and end < start:
            self.add_error('return_date', 'Return date must be on or after the booking date.')
        return data
