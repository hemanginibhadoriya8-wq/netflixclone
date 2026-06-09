# core/decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.utils import timezone
from .models import UserSubscription # Import from core's models
from django.contrib import messages

def subscription_required(view_func):
    """
    Decorator to check for an active and unexpired user subscription.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # This assumes your session_required decorator handles the login check
        # If not, you should check for request.user.is_authenticated here
        
        try:
            # Find the user's subscription object.
            # Note: This assumes you are using Django's built-in User model
            # and that your UserSubscription model has a OneToOneField to it.
            # If you are using a custom User model from core.models, this will still work.
            subscription = request.user.usersubscription
            
            # Check if the subscription is active AND the expiry date is in the future.
            if subscription.is_active and subscription.expiry_date >= timezone.now().date():
                # If the subscription is valid, let the user see the page.
                return view_func(request, *args, **kwargs)
            else:
                # If the subscription is expired or inactive, redirect them.
                messages.error(request, "Your subscription has expired. Please renew to continue watching.")
                return redirect('pricing') # Make sure you have a URL named 'pricing'
        except UserSubscription.DoesNotExist:
            # If the user has no subscription object at all, redirect them.
            messages.info(request, "You need an active subscription to watch this content.")
            return redirect('pricing')
            
    return _wrapped_view