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
