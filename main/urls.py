from django.contrib import admin
from django.urls import path
from uapfy.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),


    # organizer urls
    path('register_organizer/', register_organizer, name='register_organizer'),
    path('login_organizer/', login_organizer, name='login_organizer'),
    path('logout_organizer/', logout_organizer, name='logout_organizer'),
    path('organizer_dashboard/', dashboard, name='dashboard'),
    

    path('admin/', admin.site.urls),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()