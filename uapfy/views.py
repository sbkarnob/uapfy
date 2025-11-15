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

