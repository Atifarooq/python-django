"""
accounts/forms.py
=================
A FORM in Django does three things:
  1. Defines which fields exist (and what HTML widget to render)
  2. Validates the submitted data (server-side — cannot be bypassed)
  3. Returns cleaned, safe Python values ready to save to the database

Why not just read POST data directly?
  request.POST['email'] gives you a raw string — no validation, no safety.
  A Form automatically validates, sanitises, and gives helpful error messages.

How it works in a view:
  form = RegistrationForm(request.POST)  # Bind the submitted data
  if form.is_valid():                    # Run all validators
      email = form.cleaned_data['email'] # Safe, validated value
"""

import re  # Python's Regular Expression module — for pattern matching on strings
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  # How Django signals a validation failure

from .models import COUNTRY_CHOICES, COUNTRY_DIAL_CODES  # Import from our models file
# The dot (.) in '.models' means "look in the same package (accounts/)"


# ── Reusable validator functions ──────────────────────────────────────────────
# These are standalone functions we can attach to any form field.
# If they raise ValidationError, Django shows the message as a field error.

def validate_name(value: str, label: str) -> None:
    """
    Validates first name and last name.
    Rules:
      - Must be MORE than 3 characters (length > 3, so 4+ chars required)
      - Only letters, spaces, hyphens, apostrophes allowed
    """
    if len(value) <= 3:
        # len('abc') == 3, so 'abc' fails. 'abcd' passes.
        raise ValidationError(f'{label} must be more than 3 characters.')

    # re.fullmatch checks the ENTIRE string matches the pattern
    # [\w\s'\-]+ means: one or more of (word chars, whitespace, apostrophe, hyphen)
    # re.UNICODE makes \w match letters from any language (Arabic, French etc.)
    if not re.fullmatch(r"[\w\s'\-]+", value, re.UNICODE):
        raise ValidationError(
            f'{label} may only contain letters, spaces, hyphens, or apostrophes.'
        )


def validate_password_strength(value: str) -> None:
    """
    Validates password strength.
    Rules (all four must pass):
      - At least 8 characters
      - At least 1 uppercase letter  (A-Z)
      - At least 1 digit             (0-9)
      - At least 1 special character (anything not A-Z, a-z, 0-9)

    We collect ALL failures and report them together, so the user
    knows everything they need to fix at once.
    """
    failures = []  # Start with an empty list of problems

    if len(value) < 8:
        failures.append('at least 8 characters')

    # re.search looks for the pattern ANYWHERE in the string (not full match)
    if not re.search(r'[A-Z]', value):
        failures.append('at least 1 uppercase letter')

    if not re.search(r'[0-9]', value):
        failures.append('at least 1 number')

    # [^A-Za-z0-9] means "any character that is NOT a letter or digit"
    if not re.search(r'[^A-Za-z0-9]', value):
        failures.append('at least 1 special character')

    # Only raise an error if there were any failures
    if failures:
        raise ValidationError(
            'Password must contain ' + ', '.join(failures) + '.'
        )
        # ', '.join(['a','b','c']) → 'a, b, c'


# ── Shared widget attributes ──────────────────────────────────────────────────
# 'class': 'hfm-input' applies our CSS styling to every input field.
# This dict gets merged into each widget's attrs= parameter below.
_ATTRS = {'class': 'hfm-input'}


# ── REGISTRATION FORM ─────────────────────────────────────────────────────────

class RegistrationForm(forms.Form):
    """
    The registration form with 7 fields.

    forms.Form = a basic form (not tied to a model).
    Alternative: forms.ModelForm = auto-generates fields from a Model.
    We use forms.Form for more control over the validation logic.
    """

    # ── Field definitions ─────────────────────────────────────────────────────
    # Each field type maps to an HTML <input type="...">
    # The widget= parameter controls the HTML element rendered.
    # validators= is a list of extra validation functions to run.

    first_name = forms.CharField(
        max_length=100,  # Rejects strings longer than 100 chars
        widget=forms.TextInput(attrs={
            **_ATTRS,                        # Spread our shared CSS class
            'placeholder': 'First Name',     # Shown as grey hint text in the input
            'autocomplete': 'given-name',    # Browser autofill hint
        }),
    )

    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            **_ATTRS,
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        }),
    )

    # ChoiceField renders as <select>
    # choices= is a list of (value, label) tuples
    country = forms.ChoiceField(
        choices=[('', 'Country')] + COUNTRY_CHOICES,
        # [('', 'Country')] is the blank "Select your country" option
        # + COUNTRY_CHOICES appends US, GB, AE options after it
        widget=forms.Select(attrs={**_ATTRS}),
    )

    # HiddenInput renders as <input type="hidden">
    # The user never sees this field — it's filled by JavaScript
    # when the user selects a country.
    country_code = forms.CharField(
        max_length=6,
        widget=forms.HiddenInput(),
        required=False,  # Not required here; we validate it in clean()
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            **_ATTRS,
            'placeholder': 'Phone',
            'autocomplete': 'tel-national',
        }),
    )

    email = forms.EmailField(
        max_length=254,  # RFC 5321 max email length
        widget=forms.EmailInput(attrs={
            **_ATTRS,
            'placeholder': 'Email',
            'autocomplete': 'email',
        }),
    )

    # PasswordInput renders as <input type="password"> (dots instead of text)
    # validators= runs validate_password_strength() when this field is validated
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            **_ATTRS,
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
        validators=[validate_password_strength],  # Our custom strength checker
    )

    # ── Field-level clean methods ─────────────────────────────────────────────
    # Django automatically calls clean_<fieldname>() for each field after
    # the field's own built-in validation passes.
    # These methods must RETURN the (possibly modified) value.
    # Or raise ValidationError to reject the value.

    def clean_first_name(self):
        # .strip() removes leading/trailing whitespace the user may have typed
        value = self.cleaned_data['first_name'].strip()
        validate_name(value, 'First name')  # Runs our reusable validator
        return value  # Always return the cleaned value

    def clean_last_name(self):
        value = self.cleaned_data['last_name'].strip()
        validate_name(value, 'Last name')
        return value

    def clean_email(self):
        # .lower() normalises so 'Test@Test.COM' == 'test@test.com'
        email = self.cleaned_data['email'].strip().lower()

        # Check the database — does this email already exist?
        # filter() returns a QuerySet; .exists() returns True/False
        # __iexact means case-insensitive exact match
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email address is already registered.')

        return email

    def clean_country(self):
        value = self.cleaned_data.get('country', '')
        if not value:
            raise ValidationError('Please select your country.')
        if value not in COUNTRY_DIAL_CODES:
            raise ValidationError('Selected country is not valid.')
        return value

    def clean_country_code(self):
        code = self.cleaned_data.get('country_code', '').strip()
        if not code:
            return code  # Let clean() handle the cross-field check below
        if not code.isdigit():
            # str.isdigit() returns True only if every character is 0-9
            raise ValidationError('Country code must be numeric.')
        return code

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        # \d{6,15} means "exactly 6 to 15 digit characters"
        if not re.fullmatch(r'\d{6,15}', phone):
            raise ValidationError(
                'Phone number must be 6–15 digits with no spaces or dashes.'
            )
        return phone

    def clean(self):
        """
        clean() (no field name) runs AFTER all individual field cleaners.
        Use it for CROSS-FIELD validation (checking two fields against each other).

        Must call super().clean() first to get all individually-cleaned values.
        Use self.add_error('field_name', 'message') to attach errors to specific fields.
        """
        cleaned = super().clean()  # Runs all the clean_<field>() methods above

        # Cross-check: does the country_code match the selected country?
        country = cleaned.get('country', '')
        code    = cleaned.get('country_code', '')

        if country and code:
            expected = COUNTRY_DIAL_CODES.get(country, '')
            if code != expected:
                self.add_error(
                    'country_code',
                    f'Country code +{code} does not match the selected country '
                    f'(expected +{expected}).'
                )
        elif country and not code:
            # JS should have set this automatically; if not, fill it in server-side
            cleaned['country_code'] = COUNTRY_DIAL_CODES.get(country, '')

        return cleaned  # Always return cleaned data


# ── LOGIN FORM ────────────────────────────────────────────────────────────────

class LoginForm(forms.Form):
    """
    Simple login form — just email and password.
    We do NOT validate the password strength here because
    the user is logging in, not creating a password.
    The view handles checking credentials against the database.
    """

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            **_ATTRS,
            'placeholder': 'Email',
            'autocomplete': 'email',
        }),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            **_ATTRS,
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
    )

    # BooleanField = a checkbox
    # required=False means the form is still valid when it's unchecked
    remember_me = forms.BooleanField(required=False)

    def clean_email(self):
        # Normalise email — no validation against DB here (that's in the view)
        # This prevents "user enumeration" (attacker finding out if an email is registered)
        return self.cleaned_data['email'].strip().lower()

    def clean_password(self):
        pw = self.cleaned_data.get('password', '')
        if not pw:
            raise ValidationError('Password is required.')
        return pw
