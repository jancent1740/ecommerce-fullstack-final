# store/utils.py
from .models import Customer, Profile
from django.contrib.auth.models import User

def get_customer_for_user(user):
    """
    Return a Customer instance for the given auth.User.
    If no matching Customer exists, create one using Profile/user data.
    Returns None if user is None or not authenticated.
    """
    if not user or not user.is_authenticated:
        return None

    # Try to find a Customer by email first (preferred)
    email = getattr(user, "email", None) or ""
    if email:
        customer = Customer.objects.filter(email=email).first()
        if customer:
            return customer

    # Fallback: try to create a Customer using Profile data
    profile = Profile.objects.filter(user=user).first()
    first_name = user.first_name or (profile and getattr(profile, "first_name", "")) or ""
    last_name = user.last_name or (profile and getattr(profile, "last_name", "")) or ""
    phone = profile.phone if profile else ""

    # Create or get by username-based fake email if no email available
    fallback_email = email or f"{user.username}@example.invalid"

    customer, created = Customer.objects.get_or_create(
        email=fallback_email,
        defaults={
            "first_name": first_name or "",
            "last_name": last_name or "",
            "phone": phone or "",
            "password": ""  # keep blank for dev; don't store real passwords here
        }
    )
    return customer
