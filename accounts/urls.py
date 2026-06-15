"""
accounts/urls.py  (App-level URL file)
=======================================
This file maps URL paths to view functions within the accounts app.

path(route, view, name) takes three arguments:
  route  = the URL pattern to match (string)
  view   = the function to call when this URL is requested
  name   = a nickname for this URL (used in templates with {% url 'name' %}
           and in Python with reverse('name'))

Why 'name' matters:
  Instead of hardcoding '/login/' everywhere, you write {% url 'login' %}
  If you ever change '/login/' to '/signin/', only THIS file needs updating.
"""

from django.urls import path
from . import views  # Import all views from accounts/views.py
# The dot (.) means "current package" (accounts/)

urlpatterns = [
    # '': the root URL → registration page (http://127.0.0.1:8000/)
    path('', views.register_view, name='register'),

    # Also accessible at /register/ directly
    path('register/', views.register_view, name='register'),

    # Shown after successful registration
    path('register/success/', views.register_success_view, name='register_success'),

    # Login page
    path('login/', views.login_view, name='login'),

    # Logout — only accepts POST (form submission), not GET
    path('logout/', views.logout_view, name='logout'),

    # Dashboard — protected by @login_required in views.py
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
