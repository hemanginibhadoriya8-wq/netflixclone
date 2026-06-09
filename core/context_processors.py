# core/context_processors.py

from .models import User, UserSubscription
from django.utils import timezone

def subscription_status(request):
    user_id = request.session.get('user_id')
    
    if not user_id:
        return {'has_active_subscription': False}

    try:
       
        user = User.objects.get(id=user_id)
        subscription = user.usersubscription
        
        if subscription.is_active and subscription.expiry_date >= timezone.now().date():
            return {'has_active_subscription': True}
            
    except (User.DoesNotExist, UserSubscription.DoesNotExist):
        pass

    return {'has_active_subscription': False}