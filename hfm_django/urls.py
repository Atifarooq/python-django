"""
hfm_django/urls.py  (Project-level URL file)
=============================================
This is the MAIN URL router for the entire project.
Think of it like a post office: every incoming request
has a URL, and this file decides which app handles it.

How URLs work in Django:
  Browser requests: http://127.0.0.1:8000/login/
  Django strips the domain → '/login/'
  Django checks this file top-to-bottom for a matching pattern
  First match wins → Django calls that view function
"""

from django.contrib import admin   # Django's built-in admin site
from django.urls import path, include  # 'path' defines a URL, 'include' delegates to another file

urlpatterns = [
    # /admin/  →  Django's built-in admin panel
    # Visit http://127.0.0.1:8000/admin after creating a superuser
    path('admin/', admin.site.urls),

    # ''  →  All other URLs are handed off to accounts/urls.py
    # include() says: "read accounts/urls.py for the actual patterns"
    # This keeps URL definitions organised inside each app
    path('', include('accounts.urls')),
]
