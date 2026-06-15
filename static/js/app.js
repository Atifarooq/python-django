/**
 * static/js/app.js
 * ================
 * Front-end JavaScript: runs in the USER'S BROWSER (not on the server).
 *
 * Responsibilities:
 *   1. When the user picks a country → automatically fill in the phone code
 *   2. As the user types a password → show live rule checklist + strength bar
 *   3. Show/hide password toggle buttons
 *   4. Validate the form before submitting (client-side)
 *      NOTE: This is a UX improvement only. The server ALWAYS re-validates.
 *            A user could disable JS and bypass this entirely — that's why
 *            forms.py has the exact same rules server-side.
 *
 * IIFE (Immediately Invoked Function Expression):
 *   (function() { ... })()
 *   This wraps everything in a private scope so our variables don't
 *   accidentally clash with any other JS on the page.
 */
(function () {
    'use strict'; // Strict mode: catches common JS mistakes at runtime

    // ── Country → dial code map ───────────────────────────────────────────────
    // Must match COUNTRY_DIAL_CODES in accounts/models.py exactly
    const DIAL_CODES = {
        US:  '1',   // United States
        GB:  '44',  // United Kingdom
        AE:  '971', // United Arab Emirates
    };


    // ── UTILITY FUNCTIONS ─────────────────────────────────────────────────────

    /**
     * setError(field, message)
     * Marks a form field as invalid and shows an error message below it.
     *
     * How it works:
     *  1. Finds the parent .form-group div
     *  2. Adds the CSS class 'form-group--error' (turns border red)
     *  3. Creates a <span> with the error message below the input
     */
    function setError(field, msg) {
        const group = field.closest('.form-group'); // Walk up the DOM to find parent
        if (!group) return;

        group.classList.add('form-group--error'); // Triggers red border via CSS

        // Create a unique ID for this error span so we can find it later
        const spanId = field.id + '_fe';
        let span = document.getElementById(spanId);

        if (!span) {
            // Create the error message element if it doesn't exist yet
            span = document.createElement('span');
            span.className = 'field-error';
            span.id = spanId;
            span.setAttribute('role', 'alert'); // Screen readers announce this

            // Insert the span after the input (or after its wrapper div)
            const anchor = field.parentElement.classList.contains('pw-wrap')
                ? field.parentElement  // For password fields wrapped in .pw-wrap
                : field;
            anchor.insertAdjacentElement('afterend', span);
        }
        span.textContent = msg; // Set the message text
    }

    /**
     * clearError(field)
     * Removes the error state from a field (called when user starts correcting it).
     */
    function clearError(field) {
        const group = field.closest('.form-group');
        if (!group) return;
        group.classList.remove('form-group--error'); // Remove red border
        const span = document.getElementById(field.id + '_fe');
        if (span) span.remove(); // Remove the error message
    }

    /**
     * isEmail(value)
     * Returns true if the string looks like a valid email address.
     * Regex: one-or-more non-space/@ chars, then @, then domain, then .TLD
     */
    function isEmail(v) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
    }

    /**
     * checkPwRules(password)
     * Returns an object showing which password rules pass/fail.
     * { length: true/false, capital: true/false, number: true/false, symbol: true/false }
     */
    function checkPwRules(pw) {
        return {
            length:  pw.length >= 8,         // At least 8 characters
            capital: /[A-Z]/.test(pw),       // Contains A-Z
            number:  /[0-9]/.test(pw),       // Contains 0-9
            symbol:  /[^A-Za-z0-9]/.test(pw), // Contains anything not a letter/digit
        };
    }


    // ── FEATURE 1: Country → auto-fill phone code ─────────────────────────────

    // Django renders form fields with id="id_<fieldname>"
    // so id_country = the <select> dropdown, id_country_code = hidden input
    const countryEl  = document.getElementById('id_country');
    const codeHidden = document.getElementById('id_country_code'); // Hidden input (goes to server)
    const codeVis    = document.getElementById('code_display');    // Visible read-only input

    if (countryEl) {
        function syncCode() {
            const code = DIAL_CODES[countryEl.value] || ''; // Look up dial code
            if (codeHidden) codeHidden.value = code;         // Set hidden field for form submission
            if (codeVis)    codeVis.value    = code ? '+' + code : ''; // Show '+1' in visible field
        }

        // Listen for changes to the dropdown
        countryEl.addEventListener('change', syncCode);

        // Also run immediately — in case the page reloaded after a failed form
        // submission (the country was already selected, we need to restore the code)
        if (countryEl.value) syncCode();
    }


    // ── FEATURE 2: Live password strength checker ─────────────────────────────

    const pwInput = document.getElementById('id_password'); // The password field
    const pwBar   = document.getElementById('pw_bar');       // The strength bar div
    const pwItems = document.querySelectorAll('.pw-rule[data-rule]'); // The rule list items

    if (pwInput) {
        // 'input' event fires every time the user types a character
        pwInput.addEventListener('input', function () {
            const rules = checkPwRules(this.value);

            // Count how many rules pass (0-4)
            const score = Object.values(rules).filter(Boolean).length;

            // Width and colour for each score level
            const widths = ['0%', '25%', '50%', '75%', '100%'];
            const colors = ['transparent', '#E8192C', '#f97316', '#eab308', '#16a34a'];
            //               0 rules       1 rule       2 rules   3 rules   all 4!

            // Update the CSS custom properties on the bar element
            // The CSS uses var(--pw-w) and var(--pw-c) to animate width and colour
            if (pwBar) {
                pwBar.style.setProperty('--pw-w', widths[score]);
                pwBar.style.setProperty('--pw-c', colors[score]);
            }

            // Update each rule <li> — add/remove 'met' class (turns it green)
            // data-rule="capital" → rules.capital (true/false)
            pwItems.forEach(li => {
                li.classList.toggle('met', !!rules[li.dataset.rule]);
                // !! converts to boolean: !!undefined → false, !!true → true
            });
        });
    }


    // ── FEATURE 3: Show / hide password ──────────────────────────────────────

    // querySelectorAll returns all matching elements (there may be two eye buttons)
    document.querySelectorAll('.toggle-pw').forEach(btn => {
        btn.addEventListener('click', function () {
            // data-target="id_password" tells us which input to toggle
            const input = document.getElementById(this.dataset.target);
            if (!input) return;

            const isCurrentlyHidden = input.type === 'password';
            input.type = isCurrentlyHidden ? 'text' : 'password'; // Toggle type
            this.setAttribute('aria-label', isCurrentlyHidden ? 'Hide password' : 'Show password');
        });
    });


    // ── FEATURE 4: Registration form validation ───────────────────────────────

    const regForm = document.getElementById('registerForm');
    if (regForm) {

        regForm.addEventListener('submit', function (e) {
            let isValid = true; // Track overall validity

            // Helper: validate a name field
            function validateName(id, label) {
                const el = document.getElementById(id);
                if (!el) return;
                clearError(el);
                const v = el.value.trim();
                if (!v) {
                    setError(el, label + ' is required.');
                    isValid = false;
                } else if (v.length <= 3) {
                    setError(el, label + ' must be more than 3 characters.');
                    isValid = false;
                }
            }

            validateName('id_first_name', 'First name');
            validateName('id_last_name',  'Last name');

            // Email validation
            const emailEl = document.getElementById('id_email');
            if (emailEl) {
                clearError(emailEl);
                const v = emailEl.value.trim();
                if (!v) {
                    setError(emailEl, 'Email is required.');
                    isValid = false;
                } else if (!isEmail(v)) {
                    setError(emailEl, 'Enter a valid email (e.g. name@example.com).');
                    isValid = false;
                }
            }

            // Country validation
            const countryInput = document.getElementById('id_country');
            if (countryInput) {
                clearError(countryInput);
                if (!countryInput.value) {
                    setError(countryInput, 'Please select your country.');
                    isValid = false;
                }
            }

            // Phone validation
            const phoneEl = document.getElementById('id_phone');
            if (phoneEl) {
                clearError(phoneEl);
                const v = phoneEl.value.trim();
                if (!v) {
                    setError(phoneEl, 'Phone number is required.');
                    isValid = false;
                } else if (!/^\d{6,15}$/.test(v)) {
                    setError(phoneEl, 'Phone: 6–15 digits, no spaces or dashes.');
                    isValid = false;
                }
            }

            // Password validation
            const pwEl = document.getElementById('id_password');
            if (pwEl) {
                clearError(pwEl);
                const v = pwEl.value;
                if (!v) {
                    setError(pwEl, 'Password is required.');
                    isValid = false;
                } else {
                    const rules = checkPwRules(v);
                    const fails = [];
                    if (!rules.length)  fails.push('8+ characters');
                    if (!rules.capital) fails.push('1 uppercase letter');
                    if (!rules.number)  fails.push('1 number');
                    if (!rules.symbol)  fails.push('1 special character');
                    if (fails.length) {
                        setError(pwEl, 'Password needs: ' + fails.join(', ') + '.');
                        isValid = false;
                    }
                }
            }

            // Terms checkbox
            const terms = document.getElementById('terms');
            if (terms && !terms.checked) {
                const row = terms.closest('.checkbox-row');
                if (row) row.style.color = '#E8192C'; // Turn red
                isValid = false;
            }

            if (!isValid) {
                // Prevent the form from actually submitting
                e.preventDefault();

                // Scroll the first error into view so the user can see it
                const firstError = regForm.querySelector('.form-group--error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });

        // Live error clearing: when user starts fixing a field, remove the red error
        regForm.querySelectorAll('input, select').forEach(el => {
            el.addEventListener('input', function () {
                // Only clear if the field had an error AND now has some value
                if (this.closest('.form-group--error') && this.value.trim()) {
                    // Don't clear email error until the format is actually valid
                    if (this.id === 'id_email' && !isEmail(this.value.trim())) return;
                    clearError(this);
                }
            });
        });
    }


    // ── FEATURE 5: Login form validation ─────────────────────────────────────

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            let isValid = true;

            const emailEl = document.getElementById('id_email');
            if (emailEl) {
                clearError(emailEl);
                const v = emailEl.value.trim();
                if (!v) {
                    setError(emailEl, 'Email is required.');
                    isValid = false;
                } else if (!isEmail(v)) {
                    setError(emailEl, 'Enter a valid email (e.g. name@example.com).');
                    isValid = false;
                }
            }

            const pwEl = document.getElementById('id_password');
            if (pwEl) {
                clearError(pwEl);
                if (!pwEl.value) {
                    setError(pwEl, 'Password is required.');
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                const firstError = loginForm.querySelector('.form-group--error');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

})(); // End of IIFE — runs immediately when the browser loads this file
