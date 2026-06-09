# core/views.py
import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from core.models import User, Profile, UserSubscription, SubscriptionPlan
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from movies.models import Movie, Watchlist, WatchProgress
from series.models import Series, SeriesWatchlist, EpisodeWatchProgress 
from operator import attrgetter 
import re

# Imports needed for Razorpay
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import timedelta




def session_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'index.html')


def login(request):
    if request.session.get('user_id'):
        return redirect('home')

    if request.method == "POST":
        input_value = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.filter(email=input_value).first() or User.objects.filter(phone=input_value).first()
        if user and check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['full_name'] = user.full_name
            return redirect("profiles")
        else:
            messages.error(request, "Invalid Email/Phone Or Password")
            return redirect('login')
    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "signup.html", {"full_name": full_name, "email": email, "phone": phone})
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return render(request, "signup.html", {"full_name": full_name, "email": email, "phone": phone})
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "signup.html", {"full_name": full_name, "phone": phone})

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered")
            return render(request, "signup.html", {"full_name": full_name, "email": email})
        
        otp = random.randint(100000, 999999)
        subject = 'Your Netflix Clone Account Verification OTP'
        message = f'Hello {full_name},\n\nYour OTP for account verification is: {otp}'
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        except Exception as e:
            messages.error(request, "Failed to send verification email. Please try again.")
            return render(request, "signup.html", {"full_name": full_name, "email": email, "phone": phone})

        request.session['signup_data'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password': password,
            'otp': otp
        }
        
        return redirect('verify_otp')

    return render(request, "signup.html")

def verify_otp(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        return redirect('signup')

    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        
        if int(user_otp) == signup_data['otp']:
            new_user = User.objects.create(
                full_name=signup_data['full_name'],
                email=signup_data['email'],
                phone=signup_data['phone'],
                password=make_password(signup_data['password'])
            )
            Profile.objects.create(user=new_user, name="Netflix", avatar="avatars/4.png")
            
            del request.session['signup_data']
            
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, 'verify_otp.html')

def forgot_password(request):
    if request.method == "POST":
        email_from_form = request.POST.get("email", "").strip().lower()

        # print("--- DEBUGGING FORGOT PASSWORD ---")
        # print(f"Email entered in form: '{email_from_form}'")

        # all_users_in_db = User.objects.all()
        # print("Emails currently in the database:")
        # for u in all_users_in_db:
        #     print(f"- '{u.email.lower()}'")
        # print("---------------------------------")
    
        user = User.objects.filter(email__iexact=email_from_form).first()

        if not user:
            messages.error(request, "No account found with this email address.")
            return redirect("forgot")

        otp = random.randint(100000, 999999)
        subject = 'Your Password Reset OTP'
        message = f'Your One-Time Password (OTP) for resetting your password is: {otp}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        request.session['reset_data'] = {'email': user.email, 'otp': otp}
        return redirect('verify_reset_otp')

    return render(request, "forgot_password.html")

def verify_reset_otp(request):
    reset_data = request.session.get('reset_data')
    if not reset_data:
        return redirect('forgot')

    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        if int(user_otp) == reset_data['otp']:
            request.session['reset_verified'] = True
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, 'verify_reset_otp.html')


def reset_password(request):
    if not request.session.get('reset_verified'):
        return redirect('forgot')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'reset_password.html')

        reset_data = request.session.get('reset_data')
        user = User.objects.get(email=reset_data['email'])
        user.password = make_password(new_password)
        user.save()
        
        del request.session['reset_data']
        del request.session['reset_verified']
        
        messages.success(request, "Password has been reset successfully. Please log in.")
        return redirect('login')

    return render(request, 'reset_password.html')


@session_required
def account_settings(request):
    user = get_object_or_404(User, id=request.session.get("user_id"))
    
    # Handle profile info update
    if request.method == 'POST' and 'update_details' in request.POST:
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        
        user.full_name = full_name
        user.phone = phone
        user.save()
        messages.success(request, 'Your details have been updated.')
        return redirect('account_settings')

    # Get subscription info
    user_subscription = None
    try:
        user_subscription = user.usersubscription
    except UserSubscription.DoesNotExist:
        pass

    context = {
        'user': user,
        'user_subscription': user_subscription,
    }
    return render(request, 'account_settings.html', context)

@session_required
def change_password(request):
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.session.get("user_id"))
        
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the current password is correct
        if not check_password(current_password, user.password):
            messages.error(request, 'Your current password is incorrect.')
            return redirect('account_settings')

        # Check if the new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('account_settings')
            
        # Check for password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('account_settings')

        # If all checks pass, update the password
        user.password = make_password(new_password)
        user.save()
        messages.success(request, 'Your password has been changed successfully.')
        return redirect('account_settings')
        
    return redirect('account_settings')

@session_required
def view_profile(request):
    user_id = request.session.get("user_id")
    profile_id = request.session.get("active_profile_id")

    if not user_id or not profile_id:
        return redirect('login') 

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, id=profile_id, user=user)

    # --- 1. WATCHLIST (Movies + Series) ---
    
    # Movies ki watchlist
    movie_watchlist_items = list(Watchlist.objects.filter(profile=profile).select_related("movie"))
    
    # Series ki watchlist
    series_watchlist_items = list(SeriesWatchlist.objects.filter(profile=profile).select_related("series"))
    
    # Dono ko combine karo aur date se sort karo
    combined_watchlist = movie_watchlist_items + series_watchlist_items
    combined_watchlist.sort(key=attrgetter('added_at'), reverse=True)


    # --- 2. CONTINUE WATCHING (Movies + Series) ---

    # Movies ka progress
    continue_watching_movies = list(
        WatchProgress.objects
        .filter(user=user, profile=profile)
        .select_related("movie")
    )

    # Movies ke liye percentage calculate karo (aapka original code)
    for progress in continue_watching_movies:
        try:
            # --- YEH NAYA LOGIC HAI ---
            # Hum calculation ke liye 'actual_duration_minutes' (jaise 3) ka use karenge
            total_minutes = progress.movie.actual_duration_minutes
            
            if total_minutes is None or total_minutes == 0:
                # Agar admin mein set nahi hai, toh puraana logic try karo
                duration_str = str(progress.movie.duration).lower().strip()
                if 'h' in duration_str or 'm' in duration_str:
                    import re
                    hours = re.findall(r'(\d+)\s*h', duration_str)
                    minutes = re.findall(r'(\d+)\s*m', duration_str)
                    total_minutes = (int(hours[0]) * 60 if hours else 0) + (int(minutes[0]) if minutes else 0)
                else:
                    total_minutes = int(''.join(filter(str.isdigit, duration_str)) or 0)

            # --- END OF NAYA LOGIC ---
            
            total_seconds = total_minutes * 60
            progress.percentage = int((progress.last_position / total_seconds) * 100) if total_seconds > 0 else 0
        except Exception:
            progress.percentage = 0

    # Series (Episodes) ka progress
    continue_watching_series = list(
        EpisodeWatchProgress.objects
        .filter(user=user, profile=profile)
        .select_related("episode__season__series") # Humein series ki info bhi chahiye
    )

    # Episodes ke liye percentage calculate karo
    for progress in continue_watching_series:
        try:
            # Episode model mein duration integer hai (duration_in_minutes)
            total_seconds = progress.episode.duration_in_minutes * 60
            progress.percentage = int((progress.last_position / total_seconds) * 100) if total_seconds > 0 else 0
        except Exception:
            progress.percentage = 0

    # Dono progress lists ko combine karo aur date se sort karo
    combined_continue_watching = continue_watching_movies + continue_watching_series
    combined_continue_watching.sort(key=attrgetter('updated_at'), reverse=True)
    

    # --- 3. Subscription ---
    user_subscription = getattr(user, "usersubscription", None)

    # --- 4. Context ---
    context = {
        "profile": profile,
        "user": user,
        "continue_watching": combined_continue_watching[:10], # Sirf top 10 dikhao
        "watchlist": combined_watchlist,
        "user_subscription": user_subscription,
    }

    return render(request, "dashboard.html", context)

@session_required
def edit_profile(request):
    user = User.objects.get(id=request.session['user_id'])
    used_avatars = list(user.profiles.values_list("avatar", flat=True))
    used_names = list(user.profiles.values_list("name", flat=True))

    if request.method == "POST":
        profile_id = request.POST.get("profile_id")
        profile = get_object_or_404(Profile, id=profile_id, user=user)
        name = request.POST.get("name").strip()
        avatar = request.POST.get("avatar")

        if name in used_names and name != profile.name:
            messages.error(request, "Profile name already exists.")
            return redirect("manage")

        if avatar in used_avatars and avatar != profile.avatar:
            messages.error(request, "This avatar is already taken.")
            return redirect("manage")
        
        profile.name = name
        profile.avatar = avatar
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("manage")
    return redirect("manage")


@session_required
def delete_profile(request, profile_id):
    user = User.objects.get(id=request.session['user_id'])
    profile = get_object_or_404(Profile, id=profile_id, user=user)
    if request.method == "POST":
        profile.delete()
        messages.success(request, "Profile deleted successfully!")
        return redirect("manage")
    return redirect("manage")


@session_required
def manage_profiles(request):
    user = User.objects.get(id=request.session['user_id'])
    profiles = user.profiles.all()
    return render(request, "manage_profiles.html", {"profiles": profiles})

@session_required
def profiles(request):
    user = User.objects.get(id=request.session['user_id'])
    profiles = user.profiles.all()

    try:
        subscription = user.usersubscription
        if not subscription.is_active or subscription.expiry_date < timezone.now().date():
            profile_limit = 1
        else:
            profile_limit = subscription.plan.profile_limit
    except (UserSubscription.DoesNotExist, AttributeError):
        profile_limit = 1

    can_add_profile = profiles.count() < profile_limit

    context = {
        'profiles': profiles,
        'can_add_profile': can_add_profile
    }
    return render(request, 'profiles.html', context)

@session_required
def add_profile(request):
    user = User.objects.get(id=request.session['user_id'])
    
    try:
        subscription = user.usersubscription
        if not subscription.is_active or subscription.expiry_date < timezone.now().date():
            profile_limit = 1
        else:
            profile_limit = subscription.plan.profile_limit
    except (UserSubscription.DoesNotExist, AttributeError):
        profile_limit = 1
    
    if user.profiles.count() >= profile_limit:
        messages.error(request, "You have reached your profile limit. Please upgrade your plan to add more profiles.")
        return redirect('profiles') 
        
    used_avatars = user.profiles.values_list("avatar", flat=True)

    if request.method == "POST":
        name = request.POST.get("name")
        is_kid = request.POST.get("is_kid") == "on"
        avatar = request.POST.get("avatar", "avatars/default.png")

        if user.profiles.filter(name=name).exists():
            messages.error(request, "Profile name already exists.")
            return redirect("add_profile")

        if avatar in used_avatars:
            messages.error(request, "This avatar is already taken.")
            return redirect("add_profile")

        Profile.objects.create(user=user, name=name, is_kid=is_kid, avatar=avatar)
        return redirect("profiles")

    all_avatars = [f"avatars/{i}.png" for i in range(1, 16)]
    available_avatars = [a for a in all_avatars if a not in used_avatars]

    return render(request, "add_profile.html", {
        "available_avatars": available_avatars
    })

@session_required
def select_profile(request):
    if request.method == "POST":
        profile_id = request.POST.get("profile_id")
        user = User.objects.get(id=request.session['user_id'])
        profile = get_object_or_404(Profile, id=profile_id, user=user)
        request.session["active_profile_id"] = profile.id
        request.session["active_profile_name"] = profile.name
        request.session["active_profile_avatar"] = str(profile.avatar)
        return redirect("home")
    return redirect("profiles")


def _safe_next_url(request, fallback='home'):
    next_url = request.POST.get('next') or request.GET.get('next') or request.session.get('payment_next_url')
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback


def _activate_subscription(user, plan):
    user_subscription, created = UserSubscription.objects.get_or_create(user=user)
    user_subscription.plan = plan
    user_subscription.is_active = True
    user_subscription.expiry_date = timezone.now().date() + timedelta(days=30)
    user_subscription.save()
    return user_subscription



@session_required
def pricing(request):
    """
    This view displays subscription plans and initiates the Razorpay payment order.
    """
    plans = SubscriptionPlan.objects.all()
    user = get_object_or_404(User, id=request.session.get("user_id"))
    
    for plan in plans:
        plan.benefit_list = [benefit.strip() for benefit in plan.benefits.split(',')]
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        selected_plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        next_url = _safe_next_url(request)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount = int(selected_plan.price * 100)

        try:
            order = client.order.create(data={
                "amount": amount,
                "currency": "INR",
            })
        except Exception:
            messages.error(request, "Unable to start Razorpay checkout right now. Please try the demo payment option or check your Razorpay keys/network.")
            return redirect('pricing')

        request.session['razorpay_order_id'] = order['id']
        request.session['plan_id'] = plan_id
        request.session['payment_next_url'] = next_url

        context = {
            'order': order,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'plans': plans,
            'selected_plan': selected_plan,
            'next_url': next_url,
            'user': user,
        }
        
        return render(request, 'pricing.html', context)
    
    return render(request, 'pricing.html', {
        'plans': plans,
        'next_url': _safe_next_url(request),
        'user': user,
    })


@session_required
def demo_payment_success(request):
    if request.method != 'POST':
        return redirect('pricing')

    plan_id = request.POST.get('plan_id') or request.session.get('plan_id')
    phone = request.POST.get('phone', '').strip()
    next_url = _safe_next_url(request)

    if not phone:
        messages.error(request, "Please enter your phone number to continue.")
        return redirect('pricing')

    user = User.objects.get(id=request.session['user_id'])
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if phone != user.phone and User.objects.filter(phone=phone).exclude(id=user.id).exists():
        messages.error(request, "This phone number is already registered.")
        return redirect('pricing')

    user.phone = phone
    user.save()
    _activate_subscription(user, plan)

    request.session.pop('plan_id', None)
    request.session.pop('payment_next_url', None)
    messages.success(request, "Payment successful! Access granted.")
    return redirect(next_url)


@csrf_exempt
@session_required
def payment_success(request):
    """
    This view is called by Razorpay after a successful payment.
    It verifies the payment and activates the user's subscription.
    """
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        order_id_from_session = request.session.get('razorpay_order_id')
        plan_id = request.session.get('plan_id')

        # Check if the order ID from Razorpay matches the one in our session
        if order_id_from_session != razorpay_order_id:
            messages.error(request, "Payment verification failed. Order ID mismatch.")
            return redirect('pricing')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # If verification is successful, activate the subscription
            user = User.objects.get(id=request.session['user_id'])
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            _activate_subscription(user, plan)
            
            # Clear the session variables used for payment
            request.session.pop('razorpay_order_id', None)
            request.session.pop('plan_id', None)
            next_url = request.session.pop('payment_next_url', None)

            messages.success(request, f"Subscription to {plan.name} plan successful!")
            return redirect(next_url or 'home')

        except Exception as e:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('pricing')
            
    return redirect('pricing')


def logout(request):
    request.session.flush()
    return redirect('login')


def detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id) #This View Is For Grid
    return render(request, 'movie_detail.html', {'movie': movie})

