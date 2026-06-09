# core/management/commands/merge_db.py
from django.core.management.base import BaseCommand
from core.models import User, Profile
from movies.models import Movie, Genre, Watchlist
from series.models import Series, Season, Episode

SOURCE_DB = "source"
TARGET_DB = "default"

class Command(BaseCommand):
    help = "Merge source DB into target DB preserving IDs and episode order by id"

    def handle(self, *args, **options):
        self.stdout.write("🔷 Starting merge...")

        # ---------------- Users ----------------
        for u in User.objects.using(SOURCE_DB).all():
            if not User.objects.using(TARGET_DB).filter(id=u.id).exists():
                try:
                    User.objects.using(TARGET_DB).create(
                        id=u.id,
                        username=u.username,
                        email=u.email,
                        phone=u.phone,
                        is_staff=u.is_staff,
                        is_active=u.is_active,
                        is_superuser=u.is_superuser,
                        date_joined=u.date_joined,
                        last_login=u.last_login
                    )
                except Exception as e:
                    self.stdout.write(f"⚠ Skipping User {u.id}: {e}")

        # ---------------- Profiles ----------------
        for p in Profile.objects.using(SOURCE_DB).all():
            if not Profile.objects.using(TARGET_DB).filter(id=p.id).exists():
                if User.objects.using(TARGET_DB).filter(id=p.user_id).exists():
                    try:
                        Profile.objects.using(TARGET_DB).create(
                            id=p.id,
                            user_id=p.user_id,
                            avatar=p.avatar,
                            bio=p.bio,
                            created_at=p.created_at
                        )
                    except Exception as e:
                        self.stdout.write(f"⚠ Skipping Profile {p.id}: {e}")

        # ---------------- Genres ----------------
        for genre in Genre.objects.using(SOURCE_DB).all():
            if not Genre.objects.using(TARGET_DB).filter(id=genre.id).exists():
                Genre.objects.using(TARGET_DB).create(
                    id=genre.id,
                    name=genre.name
                )

        # ---------------- Movies ----------------
        for movie in Movie.objects.using(SOURCE_DB).all():
            if not Movie.objects.using(TARGET_DB).filter(id=movie.id).exists():
                Movie.objects.using(TARGET_DB).create(
                    id=movie.id,
                    title=movie.title,
                    description=movie.description,
                    duration_in_minutes=movie.duration_in_minutes,
                    release_date=movie.release_date,
                    thumbnail=movie.thumbnail,
                    video_file=movie.video_file
                )

        # ---------------- Watchlists ----------------
        for watch in Watchlist.objects.using(SOURCE_DB).all():
            if not Watchlist.objects.using(TARGET_DB).filter(id=watch.id).exists():
                if User.objects.using(TARGET_DB).filter(id=watch.user_id).exists() and \
                   Movie.objects.using(TARGET_DB).filter(id=watch.movie_id).exists():
                    Watchlist.objects.using(TARGET_DB).create(
                        id=watch.id,
                        user_id=watch.user_id,
                        movie_id=watch.movie_id,
                        added_at=watch.added_at
                    )

        # ---------------- Series ----------------
        for series in Series.objects.using(SOURCE_DB).all():
            if not Series.objects.using(TARGET_DB).filter(id=series.id).exists():
                Series.objects.using(TARGET_DB).create(
                    id=series.id,
                    title=series.title,
                    description=series.description,
                    thumbnail=series.thumbnail
                )

        # ---------------- Seasons ----------------
        for season in Season.objects.using(SOURCE_DB).all():
            if not Season.objects.using(TARGET_DB).filter(id=season.id).exists():
                if Series.objects.using(TARGET_DB).filter(id=season.series_id).exists():
                    Season.objects.using(TARGET_DB).create(
                        id=season.id,
                        series_id=season.series_id,
                        season_number=season.season_number,
                        description=season.description
                    )

        # ---------------- Episodes ----------------
        episodes = Episode.objects.using(SOURCE_DB).all().order_by("id")  # Sort only by id
        for ep in episodes:
            if not Episode.objects.using(TARGET_DB).filter(id=ep.id).exists():
                if Season.objects.using(TARGET_DB).filter(id=ep.season_id).exists():
                    Episode.objects.using(TARGET_DB).create(
                        id=ep.id,  # Preserve the same ID
                        season_id=ep.season_id,
                        episode_number=ep.episode_number,
                        title=ep.title,
                        description=ep.description,
                        duration_in_minutes=getattr(ep, "duration_in_minutes", 0),
                        thumbnail=getattr(ep, "thumbnail", None),
                        video_file=getattr(ep, "video_file", None)
                    )

        self.stdout.write("🎉 Merge completed successfully!")
