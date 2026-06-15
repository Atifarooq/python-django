"""
accounts/views.py
=================
A VIEW is a Python function (or class) that:
  1. Receives an HTTP request from the browser
  2. Does some work (check form data, query the database, etc.)
  3. Returns an HTTP response (usually a rendered HTML page, or a redirect)

The flow for every page visit:
  Browser → URL router (urls.py) → View function → Template → Browser

Django passes a 'request' object to every view. It contains:
  request.method      → 'GET' or 'POST'
  request.POST        → the submitted form data (dictionary)
  request.user        → the currently logged-in user (or AnonymousUser)
  request.session     → the user's session data (stored server-side)
"""

from django.shortcuts import render, redirect
# render()   → Takes a template file + context data → Returns HTML response
# redirect() → Tells the browser to go to a different URL

from django.contrib.auth import authenticate, login, logout
# authenticate() → Checks email/password against the database
#                  Returns a User object if correct, None if wrong
# login()        → Starts a session for the user (sets a cookie in their browser)
# logout()       → Destroys the session (clears the cookie)

from django.contrib.auth.models import User           # The built-in User model
from django.contrib.auth.decorators import login_required  # A decorator (explained below)
from django.db import transaction  # For atomic database operations (all-or-nothing)

from .forms import RegistrationForm, LoginForm  # Our custom forms
from .models import UserProfile, COUNTRY_DIAL_CODES


# ── REGISTRATION VIEW ─────────────────────────────────────────────────────────

def register_view(request):
    """
    Handles both:
      GET  /register/  →  Show the empty registration form
      POST /register/  →  Process the submitted form data

    The same URL handles both — the view checks request.method to know which.
    """

    # If the user is already logged in, no need to register again
    if request.user.is_authenticated:
        return redirect('dashboard')  # 'dashboard' is the name= in urls.py
        # redirect() sends the browser to a different URL

    if request.method == 'POST':
        # ── Form was submitted ─────────────────────────────────────────────
        # Bind the form to the submitted data (request.POST is a dictionary)
        form = RegistrationForm(request.POST)

        # .is_valid() runs ALL validation:
        #   1. Built-in field validation (required, max_length, email format etc.)
        #   2. Our clean_<field>() methods
        #   3. Our clean() cross-field method
        # Returns True only if everything passes
        if form.is_valid():
            # form.cleaned_data is a dictionary of safe, validated values
            # e.g. {'first_name': 'John', 'email': 'john@example.com', ...}
            cd = form.cleaned_data

            try:
                # transaction.atomic() = "all or nothing"
                # If ANY line inside fails, the entire block is rolled back.
                # This ensures we don't create a User without a Profile (or vice versa).
                with transaction.atomic():

                    # Create the Django User
                    # create_user() is a helper that hashes the password automatically
                    # We use email as the username (Django requires a username field)
                    user = User.objects.create_user(
                        username   = cd['email'],       # username must be unique
                        email      = cd['email'],
                        password   = cd['password'],    # Django hashes this for us
                        first_name = cd['first_name'],
                        last_name  = cd['last_name'],
                    )

                    # Create the UserProfile (our extra fields)
                    # This is a separate database row linked to the user above
                    UserProfile.objects.create(
                        user         = user,
                        country      = cd['country'],
                        country_code = cd['country_code'],
                        phone        = cd['phone'],
                    )

            except Exception:
                # If something unexpected went wrong (e.g. database error),
                # add a generic error to the form and show it again
                form.add_error(None, 'An unexpected error occurred. Please try again.')
            else:
                # 'else' on a try block = runs only if NO exception occurred
                # Log the new user in immediately (no need to re-enter credentials)
                login(request, user)
                return redirect('register_success')

    else:
        # ── GET request → show a blank form ───────────────────────────────
        form = RegistrationForm()

    # render() loads the template file and fills in the variables
    # 'form' is passed as a context variable → available as {{ form }} in the template
    return render(request, 'accounts/register.html', {'form': form})


def register_success_view(request):
    """
    Simple "thank you" page shown after successful registration.
    No form processing needed — just render the template.
    request.user is available in templates automatically (via context processor).
    """
    return render(request, 'accounts/register_success.html')


# ── LOGIN VIEW ────────────────────────────────────────────────────────────────

def login_view(request):
    """
    Handles the login page.
    GET  → Show empty login form
    POST → Validate credentials, start session if correct
    """

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # authenticate() looks up the user by username (=email) and
            # checks the password by hashing it and comparing to the stored hash.
            # Returns the User object on success, None on failure.
            # We NEVER reveal whether the email exists or the password is wrong
            # (both return the same generic error) — this prevents "user enumeration".
            user = authenticate(request, username=email, password=password)

            if user is None:
                # Wrong credentials → add error and show the form again
                form.add_error(None, 'Incorrect email or password. Please try again.')
            else:
                # Correct credentials → start a session
                login(request, user)

                # Session expiry:
                # set_expiry(0) = session expires when the browser closes
                # Default = session persists for SESSION_COOKIE_AGE (2 weeks by default)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)

                # If the user was redirected to login from a protected page,
                # ?next=/dashboard/ is in the URL — send them back there.
                # Otherwise, go to dashboard.
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# ── LOGOUT VIEW ───────────────────────────────────────────────────────────────

def logout_view(request):
    """
    Logs the user out and redirects to the login page.
    logout() destroys the session and clears the session cookie.
    Only accepts POST (the logout button submits a form) to prevent
    CSRF attacks where a malicious link could log a user out.
    """
    logout(request)
    return redirect('login')


# ── DASHBOARD VIEW ────────────────────────────────────────────────────────────

# @login_required is a DECORATOR.
# A decorator is a wrapper that adds behaviour to a function.
# @login_required means: "before running this view, check if the user is logged in.
#   If yes → run the view normally.
#   If no  → redirect to LOGIN_URL (/login/) automatically."
# This replaces writing 'if not request.user.is_authenticated: redirect(...)' manually.
@login_required
def dashboard_view(request):
    """
    Protected page — only accessible when logged in.
    Shows the user's account details.
    """

    # Try to get the user's profile (our extra fields)
    # request.user is the logged-in User object (set by AuthenticationMiddleware)
    # request.user.profile accesses the related UserProfile via the related_name='profile'
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Edge case: user exists but has no profile (e.g. superuser created via admin)
        profile = None

    return render(request, 'accounts/dashboard.html', {'profile': profile})
    # 'profile' is now available as {{ profile }} in the template
