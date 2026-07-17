from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify


def convert_srt_to_vtt(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    output_lines = ["WEBVTT", ""]
 HEAD
    for line in content.split("\n"):
        if line.strip().isdigit():
            continue
        if "-->" in line:
            line = line.replace(",", ".")
        output_lines.append(line)


    for line in content.split("\n"):
        stripped = line.strip()

        if stripped.isdigit():
            continue

        if "-->" in line:
            line = line.replace(",", ".")

        output_lines.append(line)

 2347441 (Improve Safari player and double tap controls)
    return "\n".join(output_lines).strip() + "\n"


def unique_slug(model, title: str, current_pk=None) -> str:
    base_slug = slugify(title) or "item"
    candidate = base_slug
    counter = 2
 HEAD
    queryset = model.objects.all()
    if current_pk:
        queryset = queryset.exclude(pk=current_pk)
    while queryset.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1


    queryset = model.objects.all()
    if current_pk:
        queryset = queryset.exclude(pk=current_pk)

    while queryset.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1

 2347441 (Improve Safari player and double tap controls)
    return candidate


class Series(models.Model):
    title = models.CharField("Series title", max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    year = models.PositiveIntegerField("Year", blank=True, null=True)
    genre = models.CharField("Genre", max_length=120, blank=True)
    description = models.TextField("Description", blank=True)
 HEAD
    poster = models.ImageField("Poster", upload_to="series/posters/", blank=True, null=True)
    backdrop = models.ImageField("Backdrop", upload_to="series/backdrops/", blank=True, null=True)


    poster = models.ImageField(
        "Poster",
        upload_to="series/posters/",
        blank=True,
        null=True,
    )

    backdrop = models.ImageField(
        "Backdrop",
        upload_to="series/backdrops/",
        blank=True,
        null=True,
    )

 2347441 (Improve Safari player and double tap controls)
    featured = models.BooleanField("Featured", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-featured", "-created_at", "title"]
        verbose_name = "Series"
        verbose_name_plural = "Series"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Series, self.title, self.pk)
 HEAD


 2347441 (Improve Safari player and double tap controls)
        super().save(*args, **kwargs)

    @property
    def episode_count(self) -> int:
        return Episode.objects.filter(season__series=self).count()

    def __str__(self):
        return self.title


class Season(models.Model):
 HEAD
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="seasons")
    number = models.PositiveIntegerField("Season number")
    title = models.CharField("Season title", max_length=220, blank=True)
    description = models.TextField("Description", blank=True)
    poster = models.ImageField("Season poster", upload_to="series/seasons/", blank=True, null=True)

    class Meta:
        ordering = ["number"]
        constraints = [models.UniqueConstraint(fields=["series", "number"], name="unique_series_season_number")]

    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="seasons",
    )

    number = models.PositiveIntegerField("Season number")
    title = models.CharField("Season title", max_length=220, blank=True)
    description = models.TextField("Description", blank=True)

    poster = models.ImageField(
        "Season poster",
        upload_to="series/seasons/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["series", "number"],
                name="unique_series_season_number",
            )
        ]
 2347441 (Improve Safari player and double tap controls)

    @property
    def display_title(self) -> str:
        return self.title or f"Season {self.number}"

    def __str__(self):
        return f"{self.series.title} — {self.display_title}"


class Episode(models.Model):
    VIDEO_TYPE_AUTO = "auto"
    VIDEO_TYPE_MP4 = "mp4"
    VIDEO_TYPE_HLS = "hls"
 HEAD
    VIDEO_TYPE_CHOICES = ((VIDEO_TYPE_AUTO, "Automatic"), (VIDEO_TYPE_MP4, "MP4"), (VIDEO_TYPE_HLS, "HLS (.m3u8)"))

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="episodes")
    number = models.PositiveIntegerField("Episode number")
    title = models.CharField("Episode title", max_length=220, blank=True)
    slug = models.SlugField(max_length=260, blank=True)
    description = models.TextField("Description", blank=True)
    duration_text = models.CharField("Duration", max_length=30, blank=True, help_text="Example: 42 min")
    thumbnail = models.ImageField("Episode thumbnail", upload_to="series/episodes/", blank=True, null=True)
    google_drive_url = models.URLField("Google Drive sharing URL", max_length=1200, blank=True)
    video_url = models.URLField("Direct MP4 or HLS URL", max_length=2000, blank=True)
    video_type = models.CharField("Video type", max_length=10, choices=VIDEO_TYPE_CHOICES, default=VIDEO_TYPE_AUTO)
    subtitle = models.FileField("Subtitle file", upload_to="series/subtitles/source/", blank=True, null=True, help_text="Upload SRT or VTT.")
    converted_subtitle = models.FileField("Converted subtitle", upload_to="series/subtitles/vtt/", blank=True, null=True, editable=False)


    VIDEO_TYPE_CHOICES = (
        (VIDEO_TYPE_AUTO, "Automatic"),
        (VIDEO_TYPE_MP4, "MP4"),
        (VIDEO_TYPE_HLS, "HLS (.m3u8)"),
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="episodes",
    )

    number = models.PositiveIntegerField("Episode number")
    title = models.CharField("Episode title", max_length=220, blank=True)
    slug = models.SlugField(max_length=260, blank=True)

    description = models.TextField("Description", blank=True)
    duration_text = models.CharField(
        "Duration",
        max_length=30,
        blank=True,
        help_text="Example: 42 min",
    )

    thumbnail = models.ImageField(
        "Episode thumbnail",
        upload_to="series/episodes/",
        blank=True,
        null=True,
    )

    google_drive_url = models.URLField(
        "Google Drive sharing URL",
        max_length=1200,
        blank=True,
    )

    video_url = models.URLField(
        "Direct MP4 or HLS URL",
        max_length=2000,
        blank=True,
    )

    video_type = models.CharField(
        "Video type",
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default=VIDEO_TYPE_AUTO,
    )

    subtitle = models.FileField(
        "Subtitle file",
        upload_to="series/subtitles/source/",
        blank=True,
        null=True,
        help_text="Upload SRT or VTT.",
    )

    converted_subtitle = models.FileField(
        "Converted subtitle",
        upload_to="series/subtitles/vtt/",
        blank=True,
        null=True,
        editable=False,
    )

 2347441 (Improve Safari player and double tap controls)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["season__number", "number"]
 HEAD
        constraints = [models.UniqueConstraint(fields=["season", "number"], name="unique_season_episode_number")]

        constraints = [
            models.UniqueConstraint(
                fields=["season", "number"],
                name="unique_season_episode_number",
            )
        ]
 2347441 (Improve Safari player and double tap controls)

    @property
    def display_title(self) -> str:
        return self.title or f"Episode {self.number}"

    @property
    def code(self) -> str:
        return f"S{self.season.number:02d}E{self.number:02d}"

    @property
    def google_drive_file_id(self) -> str:
        if not self.google_drive_url:
            return ""
 HEAD
        url = self.google_drive_url.strip()


        url = self.google_drive_url.strip()

 2347441 (Improve Safari player and double tap controls)
        if "/file/d/" in url:
            try:
                return url.split("/file/d/", 1)[1].split("/", 1)[0]
            except IndexError:
                return ""
 HEAD
        parsed = urlparse(url)
        query_id = parse_qs(parsed.query).get("id")
        return query_id[0] if query_id else ""


        parsed = urlparse(url)
        query_id = parse_qs(parsed.query).get("id")

        if query_id:
            return query_id[0]

        return ""
 2347441 (Improve Safari player and double tap controls)

    @property
    def resolved_video_type(self) -> str:
        if self.video_type != self.VIDEO_TYPE_AUTO:
            return self.video_type
 HEAD
        return self.VIDEO_TYPE_HLS if self.video_url.lower().split("?", 1)[0].endswith(".m3u8") else self.VIDEO_TYPE_MP4


        candidate = self.video_url.lower().split("?", 1)[0]

        if candidate.endswith(".m3u8"):
            return self.VIDEO_TYPE_HLS

        return self.VIDEO_TYPE_MP4
 2347441 (Improve Safari player and double tap controls)

    @property
    def source_label(self) -> str:
        if self.google_drive_url:
            return "Google Drive API streaming"
 HEAD
        if self.video_url:
            return "HLS stream" if self.resolved_video_type == self.VIDEO_TYPE_HLS else "Direct MP4"


        if self.video_url:
            return (
                "HLS stream"
                if self.resolved_video_type == self.VIDEO_TYPE_HLS
                else "Direct MP4"
            )

 2347441 (Improve Safari player and double tap controls)
        return "Not configured"

    def _convert_subtitle_file(self):
        if not self.subtitle:
            return
 HEAD
        subtitle_name = Path(self.subtitle.name).name
        extension = Path(subtitle_name).suffix.lower()


        subtitle_name = Path(self.subtitle.name).name
        extension = Path(subtitle_name).suffix.lower()

 2347441 (Improve Safari player and double tap controls)
        if extension == ".vtt":
            if self.converted_subtitle.name != self.subtitle.name:
                self.converted_subtitle = self.subtitle
                super().save(update_fields=["converted_subtitle"])
            return
 HEAD
        if extension != ".srt":
            return
        self.subtitle.open("rb")
        raw_content = self.subtitle.read()
        self.subtitle.close()
        decoded_content = None


        if extension != ".srt":
            return

        self.subtitle.open("rb")
        raw_content = self.subtitle.read()
        self.subtitle.close()

        decoded_content = None

 2347441 (Improve Safari player and double tap controls)
        for encoding in ("utf-8-sig", "utf-8", "cp1256", "windows-1256"):
            try:
                decoded_content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
 HEAD
        if decoded_content is None:
            decoded_content = raw_content.decode("utf-8", errors="replace")
        converted_name = f"{Path(subtitle_name).stem}.vtt"
        self.converted_subtitle.save(converted_name, ContentFile(convert_srt_to_vtt(decoded_content).encode("utf-8")), save=False)


        if decoded_content is None:
            decoded_content = raw_content.decode("utf-8", errors="replace")

        converted_content = convert_srt_to_vtt(decoded_content)
        converted_name = f"{Path(subtitle_name).stem}.vtt"

        self.converted_subtitle.save(
            converted_name,
            ContentFile(converted_content.encode("utf-8")),
            save=False,
        )

 2347441 (Improve Safari player and double tap controls)
        super().save(update_fields=["converted_subtitle"])

    def save(self, *args, **kwargs):
        if not self.slug:
 HEAD
            slug_title = f"{self.season.series.title}-s{self.season.number:02d}-e{self.number:02d}-{self.display_title}"
            self.slug = slugify(slug_title)

            slug_title = (
                f"{self.season.series.title}-"
                f"s{self.season.number:02d}-e{self.number:02d}-"
                f"{self.display_title}"
            )
            self.slug = slugify(slug_title)

 2347441 (Improve Safari player and double tap controls)
        super().save(*args, **kwargs)
        self._convert_subtitle_file()

    def __str__(self):
 HEAD
        return f"{self.season.series.title} — {self.code} — {self.display_title}"

        return (
            f"{self.season.series.title} — "
            f"{self.code} — {self.display_title}"
        )
 2347441 (Improve Safari player and double tap controls)
