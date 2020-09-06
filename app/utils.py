from flask import flash

def flash_form_errors(form):
    for field_name, errors in form.errors.items():
        for error in errors:
            flash(error, 'danger')

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]