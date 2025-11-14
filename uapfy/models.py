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


# Order Model
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='credit_card')
    billing_name = models.CharField(max_length=255)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20)
    billing_address = models.TextField()
    
    def __str__(self):
        return self.order_number
        
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        total = Decimal(0)
        for item in self.items.all():
            total += item.get_total()
        self.total = total
        self.save()

# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} - {self.unit_price}"
        
    def get_total(self):
        return self.quantity * self.unit_price

# Ticket Model
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='tickets', on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=255, unique=True, editable=False, db_index=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_used = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    attendee_name = models.CharField(max_length=255, blank=True, null=True)
    attendee_email = models.EmailField(blank=True, null=True)
    attendee_phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.ticket_number} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:12].upper()}"
            
        if not self.qr_code:
            qr_data = f"Ticket ID: {self.ticket_number}\nEvent: {self.event.title}\n Attendee: {self.user.username}"
            qr_img = qrcode.make(qr_data)
            blob = BytesIO()
            qr_img.save(blob, 'PNG')
            self.qr_code.save(f'{self.ticket_number}_qr.png', File(blob), save=False)
            
        super().save(*args, **kwargs)
        
    def check_in(self):
        if not self.is_used:
            self.is_used = True
            self.checked_in_at = timezone.now()
            self.save()
            return True
        return False


# Reviews Model
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'event')
        
    def __str__(self):
        return f"{self.user.username}'s review for {self.event.title}"
