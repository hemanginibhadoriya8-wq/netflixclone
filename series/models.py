# series/models.py
from django.db import models
from core.models import User, Profile
from movies.models import Genre 

class Series(models.Model):
    title = models.CharField(max_length=200, help_text="The main title of the series")
    description = models.TextField(help_text="A brief synopsis of the series")
    release_year = models.IntegerField(help_text="The year the series was first released")
    age_rating = models.CharField(max_length=10, help_text="e.g., 18+, PG-13")
    ranking = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., #5 in Series Today")
    genres = models.ManyToManyField(Genre, help_text="Select genres for this series")
    starring = models.TextField(help_text="List of main actors, separated by commas")
    creators = models.CharField(max_length=255, help_text="The creator(s) of the series")
    banner_image = models.ImageField(upload_to='series_banners/', help_text="Wide banner image for the hero section")
    trailer_video = models.FileField(upload_to='trailers/', blank=True, null=True, help_text="Optional trailer video file")

    def __str__(self):
        return self.title

class Season(models.Model):
    series = models.ForeignKey(Series, related_name='seasons', on_delete=models.CASCADE)
    season_number = models.PositiveIntegerField(help_text="The number of the season (e.g., 1, 2, 3)")
    release_date = models.DateField(blank=True, null=True, help_text="Release date of this season")

    class Meta:
        unique_together = ('series', 'season_number')

    def __str__(self):
        return f'{self.series.title} - Season {self.season_number}'

class Episode(models.Model):
    season = models.ForeignKey(Season, related_name='episodes', on_delete=models.CASCADE)
    episode_number = models.PositiveIntegerField(help_text="The number of the episode in the season")
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_in_minutes = models.PositiveIntegerField(help_text="Duration of the episode in minutes")
    thumbnail = models.ImageField(upload_to='episode_thumbnails/', help_text="Thumbnail image for the episode")
    video_file = models.FileField(upload_to='episodes/')

    def __str__(self):
        return f'{self.season} - E{self.episode_number}: {self.title}'
    
class SeriesWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'series')

    def __str__(self):
        return f'{self.profile.name}\'s list: {self.series.title}'

class EpisodeWatchProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    last_position = models.FloatField(default=0.0) # Seconds
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'episode')

    def __str__(self):
        return f'{self.profile.name} - {self.episode.title} - {self.last_position}s'