from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q 


# Create your views here.
def home(request):
    # events = Event.objects.filter(is_active=True).order_by('-start_time')[:5] 
    return render(request, 'home.html')

# User Registration
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.create(user=user)  
        messages.success(request, 'Account created successfully')
        return redirect('login')

    return render(request, 'auth/register.html')

# User Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home') 
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'auth/login.html')

# User Logout
@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

# Organizer Registration
def register_organizer(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        organization_name = request.POST['organization_name']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_organizer')

        user = User.objects.create_user(username=username, password=password, email=email)
        OrganizerProfile.objects.create(user=user, organization_name=organization_name)  
        messages.success(request, 'Organizer account created successfully')
        return redirect('login_organizer')

    return render(request, 'auth/register_organizer.html')

# Organizer Login
def login_organizer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful')
            return redirect('dashboard') 
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login_organizer')

    return render(request, 'auth/login_organizer.html')


# Organizer Logout
@login_required(login_url='login_organizer')
def logout_organizer(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login_organizer')

# Organizer Dashboard
@login_required(login_url='login_organizer')
def dashboard(request):
    organizer = get_object_or_404(OrganizerProfile, user=request.user)
    return render(request, 'dashboard/dashboard.html', { 'organizer': organizer})

# Event Creation
@login_required(login_url='login_organizer')
def event_list(request):
    organizer = get_object_or_404(OrganizerProfile, user=request.user)
    events = Event.objects.filter(organizer=organizer).order_by('-created_at')
    return render(request, 'events/event_list.html', {'events': events})

@login_required(login_url='login_organizer')
def create_event(request):
    if request.method == 'POST':
        organizer = get_object_or_404(OrganizerProfile, user=request.user)
        title = request.POST['title']
        description = request.POST['description']
        location = request.POST['location']
        venue_address = request.POST.get('venue_address', '')
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        max_attendees = request.POST.get('max_attendees', 0)
        ticket_price = request.POST.get('ticket_price', 0.00)
        category_ids = request.POST.getlist('categories')
        banner = request.FILES.get('banner')

        event = Event.objects.create(
            organizer=organizer,
            title=title,
            description=description,
            location=location,
            venue_address=venue_address,
            start_time=start_time,
            end_time=end_time,
            max_attendees=max_attendees,
            ticket_price=ticket_price,
            banner=banner
        )

        event.categories.set(category_ids)
        messages.success(request, 'Event created successfully')
        return redirect('event_list')

    categories = EventCategory.objects.all()
    return render(request, 'events/event_form.html', {'categories': categories, 'event': None})

@login_required(login_url='login_organizer')
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer__user=request.user)

    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.location = request.POST['location']
        event.venue_address = request.POST.get('venue_address', '')
        event.start_time = request.POST['start_time']
        event.end_time = request.POST['end_time']
        event.max_attendees = request.POST.get('max_attendees', 0)
        event.ticket_price = request.POST.get('ticket_price', event.ticket_price)
        event.status = request.POST.get('status', event.status)

        if 'banner' in request.FILES:
            event.banner = request.FILES['banner']

        category_ids = request.POST.getlist('categories')
        event.categories.set(category_ids)

        event.save()
        messages.success(request, 'Event updated successfully')
        return redirect('event_list')

    categories = EventCategory.objects.all()
    return render(request, 'events/event_form.html', {'event': event, 'categories': categories})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer__user=request.user)
    event.delete()
    messages.success(request, 'Event deleted successfully')
    return redirect('event_list')


# Event View  
def event_view(request):
    events = Event.objects.filter(is_active=True).order_by('-start_time')
    
    # Search functionality - NEW
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()
    
    # Category filter - NEW
    category = request.GET.get('category')
    if category:
        events = events.filter(categories__name__icontains=category)
    
    # Date filter - NEW
    date = request.GET.get('date')
    if date:
        events = events.filter(start_time__date=date)
    
    # Sort functionality - NEW
    sort = request.GET.get('sort')
    if sort == 'date_asc':
        events = events.order_by('start_time')
    elif sort == 'date_desc':
        events = events.order_by('-start_time')
    elif sort == 'price_low':
        events = events.order_by('ticket_price')
    elif sort == 'price_high':
        events = events.order_by('-ticket_price')
    elif sort == 'popular':
        # You might want to implement popularity based on ticket sales
        events = events.annotate(ticket_count=models.Count('ticket')).order_by('-ticket_count')
    
    context = {
        'events': events,
    }
    return render(request, 'events/events.html', context)

@login_required(login_url='login')
def eventdetail(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required(login_url='login')
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if max attendees limit is reached
        if event.max_attendees > 0:  # If there is a limit
            current_ticket_count = Ticket.objects.filter(event=event).count()
            if current_ticket_count + quantity > event.max_attendees:
                messages.error(request, "Sorry, this event has limited capacity and cannot accommodate your request.")
                return redirect('event_detail', event_id=event.id)
        
        # Create a new order
        order = Order.objects.create(
            user=request.user,
            subtotal=event.ticket_price * quantity,
            total=event.ticket_price * quantity,
            billing_name=request.POST.get('billing_name'),
            billing_email=request.POST.get('billing_email'),
            billing_phone=request.POST.get('billing_phone'),
            billing_address=request.POST.get('billing_address'),
            payment_method=request.POST.get('payment_method', 'credit_card')
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            event=event,
            quantity=quantity,
            unit_price=event.ticket_price
        )
        
        # Create tickets
        for _ in range(quantity):
            Ticket.objects.create(
                user=request.user,
                event=event,
                order=order,
                attendee_name=request.POST.get('attendee_name', request.user.get_full_name()),
                attendee_email=request.POST.get('attendee_email', request.user.email),
                attendee_phone=request.POST.get('attendee_phone', '')
            )
        
        # Update order status
        order.status = 'completed'
        order.save()
        
        messages.success(request, "Ticket purchase successful!")
        return redirect('my_tickets')
        
    context = {
        'event': event,
    }
    return render(request, 'ticket/buy_ticket.html', context)

@login_required(login_url='login')
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-purchased_at')
    
    context = {
        'tickets': tickets
    }
    return render(request, 'ticket/my_tickets.html', context)

@login_required(login_url='login')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    context = {
        'ticket': ticket
    }
    return render(request, 'ticket/ticket_detail.html', context)





@login_required(login_url='login_organizer')
def organizer_tickets(request):
    organizer = request.user.organizerprofile
    tickets = Ticket.objects.filter(event__organizer=organizer).select_related('event', 'user', 'order').order_by('-purchased_at')

    context = {
        'tickets': tickets,
    }
    return render(request, 'organizer/ticket_list.html', context)


@login_required(login_url='login_organizer')
def organizer_analytics(request):
    organizer = request.user.organizerprofile
    events = Event.objects.filter(organizer=organizer)
    total_events = events.count()
    total_tickets = Ticket.objects.filter(event__organizer=organizer).count()
    total_revenue = Ticket.objects.filter(event__organizer=organizer).aggregate(total=models.Sum('order__total'))['total'] or 0

    recent_tickets = Ticket.objects.filter(event__organizer=organizer).order_by('-purchased_at')[:5]

    context = {
        'total_events': total_events,
        'total_tickets': total_tickets,
        'total_revenue': total_revenue,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'organizer/analytics.html', context)
