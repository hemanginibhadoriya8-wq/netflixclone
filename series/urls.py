# series/urls.py
from django.urls import path
from . import views  

urlpatterns = [
    path('detail/<int:series_id>/', views.series_detail, name='series_detail'),
    path('play/<int:episode_id>/', views.play_episode, name='play_episode'),
    path('save-progress/', views.save_series_progress, name='save_series_progress'),
    path('watchlist/add/<int:series_id>/', views.add_to_series_watchlist, name='add_to_series_watchlist'),
    path('watchlist/remove/<int:series_id>/', views.remove_from_series_watchlist, name='remove_from_series_watchlist'),
    path('progress/remove/<int:progress_id>/', views.remove_from_series_progress, name='remove_from_series_progress'),
]
