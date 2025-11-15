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
