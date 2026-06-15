"""
accounts/models.py
==================
A MODEL is a Python class that maps directly to a database table.
Each class = one table. Each attribute = one column.

Django's ORM (Object Relational Mapper) automatically:
  - Creates the SQL table from this class (via migrations)
  - Lets you query the DB using Python instead of raw SQL
    e.g.  User.objects.filter(email='test@test.com')
    instead of:  SELECT * FROM users WHERE email = 'test@test.com'

Django already has a built-in User model with these columns:
  id, username, email, password (hashed), first_name, last_name,
  is_staff, is_active, date_joined

We EXTEND it (instead of replacing it) using a "Profile" pattern:
  One User  ←→  One UserProfile   (OneToOneField)
"""

from django.db import models
from django.contrib.auth.models import User  # Django's built-in User table


# ── Supported countries ───────────────────────────────────────────────────────
# A list of (stored_value, display_label) tuples.
# 'stored_value' is what goes in the database.
# 'display_label' is what the user sees in the <select> dropdown.

COUNTRY_CHOICES = [
    ('US', 'United States (+1)'),
    ('GB', 'United Kingdom (+44)'),
    ('AE', 'United Arab Emirates (+971)'),
]

# A plain dictionary to look up dial codes by country code.
# e.g. COUNTRY_DIAL_CODES['US'] → '1'
COUNTRY_DIAL_CODES = {
    'US': '1',
    'GB': '44',
    'AE': '971',
}


# ── UserProfile Model ─────────────────────────────────────────────────────────

class UserProfile(models.Model):
    """
    Extra fields for each user that Django's built-in User doesn't have.

    Database table name Django creates: 'accounts_userprofile'
    (format: appname_classname, all lowercase)

    Columns this creates:
      id           INTEGER  (auto primary key, added automatically)
      user_id      INTEGER  (foreign key → auth_user.id)
      country      TEXT
      country_code TEXT
      phone        TEXT
      created_at   DATETIME
    """

    # OneToOneField = "each User has exactly one Profile, and vice versa"
    # on_delete=CASCADE means: if the User is deleted, delete their Profile too
    # related_name='profile' lets you access profile from a user like: user.profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # CharField = a text column with a max length
    # choices= restricts the allowed values (shown as a dropdown in Django admin)
    country = models.CharField(
        max_length=2,         # 'US', 'GB', 'AE'
        choices=COUNTRY_CHOICES
    )

    # The numeric dial code (e.g. '1', '44', '971') — stored as text, not integer,
    # because leading zeros can matter in some countries
    country_code = models.CharField(max_length=6)

    phone = models.CharField(max_length=20)

    # auto_now_add=True: automatically set to the current datetime when the row is CREATED
    # You never need to set this manually
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # How Django labels this model in the admin panel
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        """
        __str__ controls what you see when you print a UserProfile object.
        e.g. print(profile) → "John Doe (john@example.com)"
        Django admin also uses this to label each row.
        """
        return f'{self.user.get_full_name()} ({self.user.email})'

    @property
    def full_phone(self):
        """
        @property turns a method into an attribute you can access without ()
        e.g. profile.full_phone → '+15551234567'
        instead of profile.full_phone()
        """
        return f'+{self.country_code}{self.phone}'
