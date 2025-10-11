from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from .models import CustomUser, Event, Ticket
from .forms import UserRegistrationForm, LoginForm, EventForm

# Home View
def home(request):
    events = Event.objects.filter(is_active=True)[:6]
    return render(request, 'home.html', {'events': events})

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            if user.user_type == 'organizer':
                return redirect('organizer_dashboard')
            return redirect('user_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                if user.user_type == 'organizer':
                    return redirect('organizer_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

# Dashboard Views
@login_required
def user_dashboard(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'dashboard/user_dashboard.html', {'tickets': tickets})

@login_required
def organizer_dashboard(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied.')
        return redirect('user_dashboard')
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'dashboard/organizer_dashboard.html', {'events': events})

# Event Views
@login_required
def create_event(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Organizers only.')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created!')
            return redirect('organizer_dashboard')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

def event_list(request):
    events = Event.objects.filter(is_active=True)
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.user_type == 'user':
                # Single ticket purchase
                return purchase_ticket(request, event_id)
            else:
                messages.error(request, 'Organizer accounts cannot purchase tickets.')
        else:
            messages.error(request, 'Please login to purchase tickets.')
            return redirect('login')
    
    return render(request, 'events/event_detail.html', {'event': event})

# Ticket Views
@login_required
def purchase_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user.user_type != 'user':
        messages.error(request, 'Only users can purchase tickets.')
        return redirect('event_detail', event_id=event_id)
    
    if event.available_tickets > 0:
        try:
            # Create ticket with price
            ticket = Ticket.objects.create(
                event=event,
                user=request.user,
                price_paid=event.ticket_price
            )
            
            # Update available tickets
            event.available_tickets -= 1
            event.save()
            
            messages.success(request, f'Ticket purchased successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
            
        except Exception as e:
            messages.error(request, f'Error purchasing ticket: {str(e)}')
            return redirect('event_detail', event_id=event_id)
    else:
        messages.error(request, 'Sorry, no tickets available.')
        return redirect('event_detail', event_id=event_id)

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

# Verification Views
@login_required
def verify_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            return render(request, 'verification/verification_result.html', {
                'ticket': ticket, 
                'valid': True
            })
        except Ticket.DoesNotExist:
            return render(request, 'verification/verification_result.html', {
                'valid': False, 
                'ticket_id': ticket_id
            })
    return render(request, 'verification/verify_ticket.html')

# Missing function - scan_ticket
@csrf_exempt
@login_required
def scan_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            return JsonResponse({
                'valid': True,
                'ticket': {
                    'id': str(ticket.id),
                    'event_name': ticket.event.title,
                    'customer_name': ticket.user.username,
                    'status': ticket.status,
                }
            })
        except Ticket.DoesNotExist:
            return JsonResponse({'valid': False, 'error': 'Ticket not found'})
    
    return JsonResponse({'error': 'Invalid request method'})

# Organizer Views
@login_required
def organizer_events(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied.')
        return redirect('user_dashboard')
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'events/organizer_events.html', {'events': events})

@login_required
def event_tickets(request, event_id):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied.')
        return redirect('user_dashboard')
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    tickets = Ticket.objects.filter(event=event)
    return render(request, 'events/event_tickets.html', {'event': event, 'tickets': tickets})

# API View
@csrf_exempt
@login_required
def api_verify_ticket(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            ticket = Ticket.objects.get(id=ticket_id)
            return JsonResponse({
                'success': True,
                'ticket': {
                    'id': str(ticket.id),
                    'event': ticket.event.title,
                    'customer': ticket.user.username,
                    'status': ticket.status,
                    'valid': ticket.status == 'active'
                }
            })
        except Ticket.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Ticket not found'
            })
    return JsonResponse({'error': 'Method not allowed'})
@login_required
def my_tickets(request):
    try:
        # Debug information
        print(f"User: {request.user.username}")
        print(f"User type: {request.user.user_type}")
        
        # Get tickets for the current user
        tickets = Ticket.objects.filter(user=request.user).order_by('-purchase_date')
        
        print(f"Found {tickets.count()} tickets for user {request.user.username}")
        
        # Debug: Print all tickets
        for ticket in tickets:
            print(f"Ticket: {ticket.id} - {ticket.event.title} - {ticket.status}")
        
        context = {
            'tickets': tickets
        }
        return render(request, 'tickets/my_tickets.html', context)
        
    except Exception as e:
        print(f"Error in my_tickets: {str(e)}")
        messages.error(request, f'Error loading tickets: {str(e)}')
        return render(request, 'tickets/my_tickets.html', {'tickets': []})
    
    
@login_required
def purchase_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    print(f"Purchase attempt - User: {request.user.username}, Event: {event.title}")
    
    if request.user.user_type != 'user':
        messages.error(request, 'Only users can purchase tickets.')
        return redirect('event_detail', event_id=event_id)
    
    if event.available_tickets > 0:
        try:
            # Create ticket with price
            ticket = Ticket.objects.create(
                event=event,
                user=request.user,
                price_paid=event.ticket_price
            )
            
            print(f"Ticket created: {ticket.id}")
            
            # Update available tickets
            event.available_tickets -= 1
            event.save()
            
            print(f"Available tickets updated: {event.available_tickets}")
            
            messages.success(request, f'Ticket purchased successfully! Ticket ID: {ticket.id}')
            return redirect('ticket_detail', ticket_id=ticket.id)
            
        except Exception as e:
            print(f"Error in purchase_ticket: {str(e)}")
            messages.error(request, f'Error purchasing ticket: {str(e)}')
            return redirect('event_detail', event_id=event_id)
    else:
        messages.error(request, 'Sorry, no tickets available for this event.')
        return redirect('event_detail', event_id=event_id)   \
            
@login_required
def debug_user_tickets(request):
    """Debug view to check user tickets"""
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    events_with_tickets = Event.objects.filter(ticket__user=user).distinct()
    
    context = {
        'user': user,
        'tickets': tickets,
        'total_tickets': tickets.count(),
        'events_with_tickets': events_with_tickets,
        'all_events': Event.objects.all()[:5]  # Show first 5 events for reference
    }
    return render(request, 'debug/user_tickets.html', context)