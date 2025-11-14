from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
import uuid
from decimal import Decimal


# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    

    # Organizer Profile
class OrganizerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    organization_address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    logo = models.ImageField(upload_to='organizer_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.organization_name or self.user.username

# Event Category
class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


# Event Model
class Event(models.Model):
    EVENT_STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    organizer = models.ForeignKey(OrganizerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    location = models.CharField(max_length=255)
    venue_address = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(EventCategory, related_name='events')
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='upcoming')
    featured = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(default=0)  # 0 means unlimited
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    
    def __str__(self):
        return self.title
        
    def update_status(self):
        now = timezone.now()
        if self.start_time and self.end_time:
            if now < self.start_time:
                self.status = 'upcoming'
            elif self.start_time <= now <= self.end_time:
                self.status = 'ongoing'
            elif now > self.end_time:
                self.status = 'completed'
            self.save()
