import re
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

# E-Mail-Regex
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email_format(email: str):
    """Prüft das Format einer E-Mail-Adresse."""
    if not re.match(EMAIL_REGEX, email):
        raise ValidationError({"email": "Ungültige E-Mail-Adresse."})


def validate_email_unique(email: str):
    """Prüft, ob die E-Mail bereits vergeben ist."""
    if User.objects.filter(email=email).exists():
        raise ValidationError(
            {"email": "E-Mail-Adresse wird bereits verwendet."})


def validate_fullname(fullname: str):
    """Prüft, ob Fullname aus mindestens zwei Teilen besteht."""
    if not fullname or len(fullname.strip().split()) < 2:
        raise ValidationError({"fullname": "Bitte Vor- und Nachname angeben."})


def validate_password_strength(password: str):
    """Prüft die Passwort-Sicherheit."""
    if len(password) < 8:
        raise ValidationError(
            {"password": "Passwort muss mindestens 8 Zeichen lang sein."})
    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            {"password": "Mindestens ein Großbuchstabe erforderlich."})
    if not re.search(r"[a-z]", password):
        raise ValidationError(
            {"password": "Mindestens ein Kleinbuchstabe erforderlich."})
    if not re.search(r"\d", password):
        raise ValidationError(
            {"password": "Mindestens eine Zahl erforderlich."})
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError(
            {"password": "Mindestens ein Sonderzeichen erforderlich."})
