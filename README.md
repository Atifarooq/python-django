# HFM Django Project – Beginner's Guide

---

## 1. What is Django?

Django is a **web framework** written in Python.
A framework gives you a pre-built structure so you don't have to
write the same boilerplate (routing, database access, security) from scratch.

Django follows the **MVT pattern**:

```
MVT = Model · View · Template

Model    → Python class that represents a database table
View     → Python function that processes a request and returns a response
Template → HTML file with special Django tags for displaying data
```

---

## 2. Project vs App

Django separates code into two levels:

```
PROJECT  = the entire website configuration
APP      = a self-contained module of functionality
```

A project can have many apps. Our project has one: `accounts`.

Think of it like this:
- **Project** = a restaurant (has settings, opening hours, location)
- **App**     = the kitchen (handles one specific job: making food)

---

## 3. Folder Structure — What Every File Does

```
hfm_django/                     ← Project root (where you run commands)
│
├── manage.py                   ← Django's command-line tool
│                                 Run: python manage.py runserver
│                                      python manage.py migrate
│                                      python manage.py createsuperuser
│
├── requirements.txt            ← Python packages to install (just Django)
│                                 Run: pip install -r requirements.txt
│
├── db/
│   └── hfm.sqlite3             ← The actual database FILE (created after migrate)
│                                 This is your entire database in one file!
│
├── hfm_django/                 ← Project configuration package
│   ├── __init__.py             ← Tells Python "this folder is a package" (empty)
│   ├── settings.py             ← ALL project settings (database, installed apps, etc.)
│   ├── urls.py                 ← Root URL router → directs traffic to the right app
│   └── wsgi.py                 ← Entry point for production web servers (Nginx, Apache)
│
├── accounts/                   ← Our custom app (handles users)
│   ├── __init__.py             ← Empty file, marks this as a Python package
│   ├── models.py               ← Database table definitions (UserProfile)
│   ├── forms.py                ← Form fields + server-side validation rules
│   ├── views.py                ← Request handlers (register, login, logout, dashboard)
│   ├── urls.py                 ← URL patterns for this app
│   ├── admin.py                ← Registers models in the /admin panel
│   ├── apps.py                 ← App configuration (name, settings)
│   └── migrations/             ← Auto-generated database migration files
│       ├── __init__.py
│       └── 0001_initial.py     ← Creates the UserProfile table in the database
│
│   templates/accounts/         ← HTML template files for this app
│       ├── base.html           ← Shared layout (header, footer, CSS links)
│       ├── register.html       ← Registration page (extends base.html)
│       ├── register_success.html ← "Thank you" page
│       ├── login.html          ← Login page
│       └── dashboard.html      ← Protected account page
│
└── static/                     ← CSS, JavaScript, images
    ├── css/
    │   └── style.css           ← All styling for the entire project
    └── js/
        └── app.js              ← All front-end JavaScript
```

---

## 4. How a Request Travels Through Django

Let's trace what happens when a user visits `http://127.0.0.1:8000/login/`:

```
Step 1: Browser sends GET request to /login/

Step 2: Django reads hfm_django/urls.py
        → Finds: path('', include('accounts.urls'))
        → Passes /login/ to accounts/urls.py

Step 3: Django reads accounts/urls.py
        → Finds: path('login/', views.login_view, name='login')
        → Calls the login_view() function

Step 4: login_view() in views.py runs
        → request.method == 'GET'
        → Creates empty LoginForm()
        → Calls render(request, 'accounts/login.html', {'form': form})

Step 5: Django finds accounts/templates/accounts/login.html
        → login.html extends base.html (inherits the header etc.)
        → Fills in {{ form.email }}, {{ form.password }} etc.
        → Returns the completed HTML

Step 6: Browser receives HTML and displays the page
```

Now what happens when the user **submits** the form:

```
Step 1: Browser sends POST request to /login/ with:
        { email: 'john@example.com', password: 'Secret1!' }

Step 2-3: Same URL routing as above → login_view()

Step 4: login_view() runs
        → request.method == 'POST'
        → form = LoginForm(request.POST)  ← binds submitted data
        → form.is_valid()                 ← runs all validators

Step 5a: If validation FAILS
        → render the login page again with form.errors shown

Step 5b: If validation PASSES
        → authenticate(email, password) → check against database
        → If wrong: add error, show form again
        → If correct: login(request, user) → set session cookie
        → redirect('dashboard') → browser goes to /dashboard/
```

---

## 5. The Database — Models & Migrations

### What is a Migration?

When you define a Model in models.py, Django doesn't immediately create
the database table. You need to run two commands:

```bash
# Step 1: Django reads your models and generates a migration FILE
python manage.py makemigrations

# Step 2: Django APPLIES the migration (runs SQL to create/alter tables)
python manage.py migrate
```

The migration file in `accounts/migrations/0001_initial.py` is auto-generated
SQL instructions written as Python. You rarely need to edit them.

### Our Database Tables

After running `migrate`, two tables exist for user data:

```
auth_user                    ← Django's built-in
  id
  username  (= email in our case)
  email
  password  (NEVER plain text — stored as hash)
  first_name
  last_name
  is_staff
  date_joined

accounts_userprofile         ← Our extension
  id
  user_id   (points to auth_user.id)
  country
  country_code
  phone
  created_at
```

They're linked: each row in `accounts_userprofile` points to exactly
one row in `auth_user` via the `user_id` column.

---

## 6. Forms — The Validation Pipeline

When a form is submitted, Django runs validators in this order:

```
1. Field-level built-in checks
   (Is it required? Is it within max_length? Is it a valid email format?)

2. Field-level custom clean methods
   clean_first_name() → validate_name()
   clean_email()      → check DB for duplicates
   clean_password()   → validate_password_strength()
   etc.

3. Cross-field clean()
   Are passwords matching?
   Does country_code match the selected country?

4. If all pass → form.is_valid() returns True
   form.cleaned_data = { 'email': 'john@test.com', ... }

5. If any fail → form.is_valid() returns False
   form.errors = { 'email': ['This email is already registered.'] }
   The template loops over errors and shows them under each field.
```

---

## 7. Templates — Django's HTML System

Templates are HTML files with extra Django syntax:

```django
{{ variable }}           ← Output a variable (auto-escaped to prevent XSS)
{% tag %}                ← Logic (if, for, block, extends, url, csrf_token)
{{ variable|filter }}   ← Transform a value (e.g. {{ date|date:"Y-m-d" }})
```

### Template Inheritance

`base.html` contains the shared structure (header, CSS links, JS links).
Other templates "extend" it instead of copy-pasting the header.

```
base.html defines:
  {% block title %}...{% endblock %}   ← child can replace this
  {% block header_cta %}...{% endblock %}
  {% block main %}...{% endblock %}

register.html does:
  {% extends "accounts/base.html" %}   ← inherit everything from base
  {% block title %}Register{% endblock %} ← override just the title
  {% block main %}...form here...{% endblock %}
```

### The {% csrf_token %} Tag

Every POST form must include `{% csrf_token %}`.
Django generates a hidden input with a random token that it checks
on submission. This prevents Cross-Site Request Forgery attacks
(where a malicious website tricks your browser into submitting a form).

```html
<form method="POST">
  {% csrf_token %}   ← REQUIRED in every form
  ...
</form>
```

---

## 8. Static Files (CSS & JavaScript)

Files in the `static/` folder are served at the `/static/` URL prefix.

In templates, always use `{% static %}` instead of hardcoded paths:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

This generates: `/static/css/style.css`

Why? In production, `collectstatic` copies all static files to one place,
possibly on a CDN. The `{% static %}` tag handles the URL change automatically.

---

## 9. Setup & Running

```bash
# 1. Install Django (and bcrypt if desired)
pip install -r requirements.txt

# 2. Create the db/ directory
mkdir -p db

# 3. Apply migrations (creates hfm.sqlite3 and all tables)
python manage.py migrate

# 4. Create an admin superuser (optional — for /admin panel)
python manage.py createsuperuser

# 5. Start the development server
python manage.py runserver

# Now open: http://127.0.0.1:8000
```

---

## 10. Key Django Commands Reference

| Command | What it does |
|---|---|
| `python manage.py runserver` | Start dev server at localhost:8000 |
| `python manage.py migrate` | Apply pending migrations to the database |
| `python manage.py makemigrations` | Generate migration files after editing models.py |
| `python manage.py createsuperuser` | Create an admin user for /admin |
| `python manage.py shell` | Open a Python shell with Django loaded (great for testing) |
| `python manage.py collectstatic` | Copy static files to STATIC_ROOT (production) |

---

## 11. Security Summary

| Threat | How we stop it |
|---|---|
| **SQL Injection** | Django ORM — never write raw SQL; all queries are parameterised |
| **XSS** (Cross-Site Scripting) | Django auto-escapes all `{{ variables }}` in templates |
| **CSRF** (Cross-Site Request Forgery) | `{% csrf_token %}` in every form + CsrfViewMiddleware |
| **Password exposure** | `create_user()` and `set_password()` always hash; never stored plain |
| **Session hijacking** | `SESSION_COOKIE_HTTPONLY=True` — JS cannot read the cookie |
| **Clickjacking** | `XFrameOptionsMiddleware` sets `X-Frame-Options: DENY` |
| **User enumeration** | Login returns same error whether email is wrong OR password is wrong |
