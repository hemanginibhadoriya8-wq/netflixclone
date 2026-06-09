from django.db import models

class User(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    name = models.CharField(max_length=100)
    is_kid = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")

    def __str__(self):
        return f"{self.name} ({'Kid' if self.is_kid else 'Adult'})"
    
    
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    profile_limit = models.PositiveIntegerField(default=1)
    benefits = models.TextField(help_text="List of benefits, separated by commas")
    screens = models.PositiveIntegerField(default=1, help_text="How many screens can watch at the same time")

    def __str__(self):
        return self.name
    
    
class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name}'s Subscription"
