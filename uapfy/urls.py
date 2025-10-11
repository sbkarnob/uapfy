from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<uuid:event_id>/', views.event_detail, name='event_detail'),
    
    # Authentication URLs
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.user_login, name='login'),
    path('auth/logout/', views.user_logout, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    
    # Event URLs
    path('events/create/', views.create_event, name='create_event'),
    path('events/<uuid:event_id>/purchase/', views.purchase_ticket, name='purchase_ticket'),
    path('organizer/events/', views.organizer_events, name='organizer_events'),
    path('events/<uuid:event_id>/tickets/', views.event_tickets, name='event_tickets'),
    
    # Ticket URLs
    path('tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # Verification URLs
    path('verify/', views.verify_ticket, name='verify_ticket'),
    path('scan/<uuid:ticket_id>/', views.scan_ticket, name='scan_ticket'),
    path('api/verify-ticket/', views.api_verify_ticket, name='api_verify_ticket'),
    path('debug/tickets/', views.debug_user_tickets, name='debug_tickets'),
]