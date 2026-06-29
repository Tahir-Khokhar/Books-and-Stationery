"""Book_and_Stationery URL configuration."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('items.urls')),
    path('accounts/', include('items.urls')), 
]




