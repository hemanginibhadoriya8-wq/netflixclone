from django.contrib import admin
from .models import User , Profile , SubscriptionPlan , UserSubscription

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "created_at")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "is_kid", "avatar")
    
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'profile_limit')
    list_display = ('name', 'price', 'profile_limit', 'screens')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active')
    list_filter = ('plan', 'is_active')
