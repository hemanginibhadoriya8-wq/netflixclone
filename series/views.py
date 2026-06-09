# series/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Series, Season, Episode, SeriesWatchlist, EpisodeWatchProgress
from core.models import User, Profile, UserSubscription
from core.views import session_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import json

@session_required
def series_detail(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    profile = get_object_or_404(Profile, id=request.session.get('active_profile_id'))
    user_subscription = getattr(profile.user, "usersubscription", None)
    has_active_subscription = user_subscription and user_subscription.is_active
    first_episode = None
    first_season = series.seasons.order_by('season_number').first()
    if first_season:
        first_episode = first_season.episodes.order_by('episode_number').first()

    context = {
        'series': series,
        'first_episode': first_episode,
        'has_active_subscription': has_active_subscription,
    }
    return render(request, 'series_detail.html', context)

@never_cache
@session_required
def play_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    profile = get_object_or_404(Profile, id=request.session.get('active_profile_id'))
    progress = EpisodeWatchProgress.objects.filter(profile=profile, episode=episode).first()
    start_position = progress.last_position if progress else 0.0

    context = {
        'episode': episode,
        'start_position': start_position
    }
    return render(request, 'play_episode.html', context)

@csrf_exempt
@session_required
def save_series_progress(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            episode_id = data.get('episode_id')
            position = data.get('position')
            
            user = get_object_or_404(User, id=request.session.get('user_id'))
            profile = get_object_or_404(Profile, id=request.session.get('active_profile_id'))
            episode = get_object_or_404(Episode, id=episode_id)

            progress, created = EpisodeWatchProgress.objects.update_or_create(
                user=user,
                profile=profile,
                episode=episode,
                defaults={'last_position': position}
            )
            return JsonResponse({'status': 'success', 'saved_at': position})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@session_required
def remove_from_series_progress(request, progress_id):
    user_id = request.session.get('user_id')
    profile_id = request.session.get('active_profile_id')
    
    if not user_id or not profile_id:
        return redirect("login")
    
    progress_to_delete = get_object_or_404(
        EpisodeWatchProgress, 
        id=progress_id, 
        user_id=user_id, 
        profile_id=profile_id
    )

    series_title = progress_to_delete.episode.season.series.title    
    progress_to_delete.delete()
    messages.success(request, f'"{series_title}" was removed from Continue Watching.')
    
    return redirect('view')


@session_required
def add_to_series_watchlist(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    user = get_object_or_404(User, id=request.session.get('user_id'))
    profile = get_object_or_404(Profile, id=request.session.get('active_profile_id'))

    is_in_watchlist, created = SeriesWatchlist.objects.get_or_create(
        user=user, profile=profile, series=series
    )

    if created:
        messages.success(request, f'{series.title} added to your list.')
    else:
        messages.info(request, f'{series.title} is already in your list.')
    
    return redirect("home")

@session_required
def remove_from_series_watchlist(request, series_id):
    user_id = request.session.get("user_id")
    profile_id = request.session.get("active_profile_id")

    if not user_id or not profile_id:
        return redirect("login")

    try:
        watchlist_item = SeriesWatchlist.objects.get(
            user_id=user_id, 
            profile_id=profile_id, 
            series_id=series_id
        )
        watchlist_item.delete()
        messages.success(request, "Series removed from Watchlist.")
    except SeriesWatchlist.DoesNotExist:
        messages.warning(request, "Series not found in your Watchlist.")

    return redirect("view")