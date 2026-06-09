from django.urls import path
from . import views

urlpatterns = [
    #This 3 Urls For Login Signing Up Loging Out And Index Page
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('index/', views.index, name='home'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password/',views.forgot_password, name="forgot"),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('account/', views.account_settings, name='account_settings'),
    path('account/change-password/', views.change_password, name='change_password'),

    #This 2 Urls For Profile's Page
    path('profiles/', views.profiles, name='profiles'),
    path('view_profile/', views.view_profile, name='view'),
    path("profiles/add/", views.add_profile, name="add_profile"),
    path("profiles/select/", views.select_profile, name="select_profile"),
    path("manage_profiles/", views.manage_profiles, name="manage"),
    path("profiles/edit/", views.edit_profile, name="edit_profile"),
    path("profiles/delete/<int:profile_id>/", views.delete_profile, name="delete_profile"),
    


    #This Urls For Subscription
    path('pricing/', views.pricing, name='pricing'), 
    path('payment-success/', views.payment_success, name='payment_success'),
    path('demo-payment-success/', views.demo_payment_success, name='demo_payment_success'),
   

    #This Urls Will Work For Movie Page
    path('movie_detail/<int:movie_id>/', views.detail, name="moviedetail"),
    

]
