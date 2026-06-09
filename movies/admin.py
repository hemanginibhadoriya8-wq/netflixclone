from django.contrib import admin
from .models import Movie, Genre , Category , Watchlist , WatchProgress

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "imdb_rating", "age_limit", "release_year", "created_at")
    search_fields = ("title", "starring", "tags")
    list_filter = ("age_limit", "release_year", "genres","categories")

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "profile", "movie", "added_at")   
    list_filter = ("user", "profile", "movie")
    search_fields = ("movie__title", "user__username", "profile__name")

@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ('profile', 'movie', 'last_position', 'updated_at')
    list_filter = ('profile', 'movie')
    search_fields = ('movie__title', 'profile__name')
