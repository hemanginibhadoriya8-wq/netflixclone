# series/admin.py
from django.contrib import admin
from .models import Series, Season, Episode , SeriesWatchlist , EpisodeWatchProgress

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "age_rating", "ranking")
    search_fields = ("title", "creators", "starring")
    list_filter = ("release_year", "age_rating", "genres")

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("series", "season_number", "release_date")
    search_fields = ("series__title",)
    list_filter = ("series",)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "season", "episode_number", "duration_in_minutes")
    search_fields = ("title", "season__series__title")
    list_filter = ("season__series", "season")
    
@admin.register(SeriesWatchlist)
class SeriesWatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile', 'series', 'added_at')
    list_filter = ('user', 'profile')
    search_fields = ('series__title', 'profile__name', 'user__username')

@admin.register(EpisodeWatchProgress)
class EpisodeWatchProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile', 'episode', 'last_position', 'updated_at')
    list_filter = ('user', 'profile')
    search_fields = ('episode__title', 'profile__name', 'user__username')