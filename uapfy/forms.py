from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Event
from django.core.exceptions import ValidationError
import datetime

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='user',
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'venue', 'event_date', 'ticket_price', 'total_tickets']
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < datetime.datetime.now().replace(tzinfo=event_date.tzinfo):
            raise ValidationError("Event date cannot be in the past.")
        return event_date
    
    def clean_total_tickets(self):
        total_tickets = self.cleaned_data.get('total_tickets')
        if total_tickets and total_tickets <= 0:
            raise ValidationError("Total tickets must be greater than 0.")
        return total_tickets

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)