from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Series",
            fields=[
 HEAD
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=220, verbose_name="Series title")),
                ("slug", models.SlugField(blank=True, max_length=240, unique=True)),
                ("year", models.PositiveIntegerField(blank=True, null=True, verbose_name="Year")),
                ("genre", models.CharField(blank=True, max_length=120, verbose_name="Genre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("poster", models.ImageField(blank=True, null=True, upload_to="series/posters/", verbose_name="Poster")),
                ("backdrop", models.ImageField(blank=True, null=True, upload_to="series/backdrops/", verbose_name="Backdrop")),
                ("featured", models.BooleanField(default=False, verbose_name="Featured")),
                ("created_at", models.DateTimeField(auto_now_add=True)),

                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=220,
                        verbose_name="Series title",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        max_length=240,
                        unique=True,
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Year",
                    ),
                ),
                (
                    "genre",
                    models.CharField(
                        blank=True,
                        max_length=120,
                        verbose_name="Genre",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        verbose_name="Description",
                    ),
                ),
                (
                    "poster",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="series/posters/",
                        verbose_name="Poster",
                    ),
                ),
                (
                    "backdrop",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="series/backdrops/",
                        verbose_name="Backdrop",
                    ),
                ),
                (
                    "featured",
                    models.BooleanField(
                        default=False,
                        verbose_name="Featured",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
 2347441 (Improve Safari player and double tap controls)
            ],
            options={
                "verbose_name": "Series",
                "verbose_name_plural": "Series",
 HEAD
                "ordering": ["-featured", "-created_at", "title"],

                "ordering": [
                    "-featured",
                    "-created_at",
                    "title",
                ],
 2347441 (Improve Safari player and double tap controls)
            },
        ),
        migrations.CreateModel(
            name="Season",
            fields=[
 HEAD
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveIntegerField(verbose_name="Season number")),
                ("title", models.CharField(blank=True, max_length=220, verbose_name="Season title")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("poster", models.ImageField(blank=True, null=True, upload_to="series/seasons/", verbose_name="Season poster")),
                ("series", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seasons", to="series.series")),
            ],
            options={"ordering": ["number"]},

                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "number",
                    models.PositiveIntegerField(
                        verbose_name="Season number",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        max_length=220,
                        verbose_name="Season title",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        verbose_name="Description",
                    ),
                ),
                (
                    "poster",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="series/seasons/",
                        verbose_name="Season poster",
                    ),
                ),
                (
                    "series",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seasons",
                        to="series.series",
                    ),
                ),
            ],
            options={
                "ordering": ["number"],
            },
 2347441 (Improve Safari player and double tap controls)
        ),
        migrations.CreateModel(
            name="Episode",
            fields=[
 HEAD
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveIntegerField(verbose_name="Episode number")),
                ("title", models.CharField(blank=True, max_length=220, verbose_name="Episode title")),
                ("slug", models.SlugField(blank=True, max_length=260)),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("duration_text", models.CharField(blank=True, help_text="Example: 42 min", max_length=30, verbose_name="Duration")),
                ("thumbnail", models.ImageField(blank=True, null=True, upload_to="series/episodes/", verbose_name="Episode thumbnail")),
                ("google_drive_url", models.URLField(blank=True, max_length=1200, verbose_name="Google Drive sharing URL")),
                ("video_url", models.URLField(blank=True, max_length=2000, verbose_name="Direct MP4 or HLS URL")),
                ("video_type", models.CharField(choices=[("auto", "Automatic"), ("mp4", "MP4"), ("hls", "HLS (.m3u8)")], default="auto", max_length=10, verbose_name="Video type")),
                ("subtitle", models.FileField(blank=True, help_text="Upload SRT or VTT.", null=True, upload_to="series/subtitles/source/", verbose_name="Subtitle file")),
                ("converted_subtitle", models.FileField(blank=True, editable=False, null=True, upload_to="series/subtitles/vtt/", verbose_name="Converted subtitle")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("season", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="episodes", to="series.season")),
            ],
            options={"ordering": ["season__number", "number"]},
        ),
        migrations.AddConstraint(
            model_name="season",
            constraint=models.UniqueConstraint(fields=("series", "number"), name="unique_series_season_number"),
        ),
        migrations.AddConstraint(
            model_name="episode",
            constraint=models.UniqueConstraint(fields=("season", "number"), name="unique_season_episode_number"),

                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "number",
                    models.PositiveIntegerField(
                        verbose_name="Episode number",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        max_length=220,
                        verbose_name="Episode title",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        max_length=260,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        verbose_name="Description",
                    ),
                ),
                (
                    "duration_text",
                    models.CharField(
                        blank=True,
                        help_text="Example: 42 min",
                        max_length=30,
                        verbose_name="Duration",
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="series/episodes/",
                        verbose_name="Episode thumbnail",
                    ),
                ),
                (
                    "google_drive_url",
                    models.URLField(
                        blank=True,
                        max_length=1200,
                        verbose_name="Google Drive sharing URL",
                    ),
                ),
                (
                    "video_url",
                    models.URLField(
                        blank=True,
                        max_length=2000,
                        verbose_name="Direct MP4 or HLS URL",
                    ),
                ),
                (
                    "video_type",
                    models.CharField(
                        choices=[
                            ("auto", "Automatic"),
                            ("mp4", "MP4"),
                            ("hls", "HLS (.m3u8)"),
                        ],
                        default="auto",
                        max_length=10,
                        verbose_name="Video type",
                    ),
                ),
                (
                    "subtitle",
                    models.FileField(
                        blank=True,
                        help_text="Upload SRT or VTT.",
                        null=True,
                        upload_to="series/subtitles/source/",
                        verbose_name="Subtitle file",
                    ),
                ),
                (
                    "converted_subtitle",
                    models.FileField(
                        blank=True,
                        editable=False,
                        null=True,
                        upload_to="series/subtitles/vtt/",
                        verbose_name="Converted subtitle",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="episodes",
                        to="series.season",
                    ),
                ),
            ],
            options={
                "ordering": [
                    "season__number",
                    "number",
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="season",
            constraint=models.UniqueConstraint(
                fields=("series", "number"),
                name="unique_series_season_number",
            ),
        ),
        migrations.AddConstraint(
            model_name="episode",
            constraint=models.UniqueConstraint(
                fields=("season", "number"),
                name="unique_season_episode_number",
            ),
 2347441 (Improve Safari player and double tap controls)
        ),
    ]
