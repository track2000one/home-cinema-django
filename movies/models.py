from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify


def convert_srt_to_vtt(content: str) -> str:
    """Convert common SRT subtitle content into WebVTT."""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    output_lines = ["WEBVTT", ""]

    for line in content.split("\n"):
        stripped = line.strip()

        if stripped.isdigit():
            continue

        if "-->" in line:
            line = line.replace(",", ".")

        output_lines.append(line)

    return "\n".join(output_lines).strip() + "\n"


class Movie(models.Model):
    VIDEO_TYPE_AUTO = "auto"
    VIDEO_TYPE_MP4 = "mp4"
    VIDEO_TYPE_HLS = "hls"

    VIDEO_TYPE_CHOICES = (
        (VIDEO_TYPE_AUTO, "Automatic"),
        (VIDEO_TYPE_MP4, "MP4"),
        (VIDEO_TYPE_HLS, "HLS (.m3u8)"),
    )

    title = models.CharField("Title", max_length=220)

    slug = models.SlugField(
        max_length=240,
        unique=True,
        blank=True,
    )

    year = models.PositiveIntegerField(
        "Year",
        blank=True,
        null=True,
    )

    genre = models.CharField(
        "Genre",
        max_length=120,
        blank=True,
    )

    description = models.TextField(
        "Description",
        blank=True,
    )

    poster = models.ImageField(
        "Poster",
        upload_to="posters/",
        blank=True,
        null=True,
    )

    video_path = models.CharField(
        "Local video file path",
        max_length=1000,
        blank=True,
        help_text=r"Local development only. Example: E:\Movies\film.mp4",
    )

    video_url = models.URLField(
        "Direct MP4 or HLS URL",
        max_length=2000,
        blank=True,
        help_text=(
            "Preferred for Railway. Enter a direct .mp4 URL or an "
            "HLS .m3u8 playlist URL."
        ),
    )

    video_type = models.CharField(
        "Video type",
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default=VIDEO_TYPE_AUTO,
    )

    google_drive_url = models.URLField(
        "Google Drive sharing URL",
        max_length=1000,
        blank=True,
        help_text=(
            "Transitional option. Direct MP4/HLS hosting is more reliable "
            "for seeking, mobile playback, and high traffic."
        ),
    )

    subtitle = models.FileField(
        "Subtitle file",
        upload_to="subtitles/source/",
        blank=True,
        null=True,
        help_text="Upload an SRT or VTT subtitle file.",
    )

    converted_subtitle = models.FileField(
        "Converted subtitle",
        upload_to="subtitles/vtt/",
        blank=True,
        null=True,
        editable=False,
    )

    featured = models.BooleanField(
        "Featured",
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-featured",
            "-created_at",
            "title",
        ]

    def clean(self):
        super().clean()

        configured_sources = [
            bool(self.video_path),
            bool(self.video_url),
            bool(self.google_drive_url),
        ]

        if not any(configured_sources):
            raise ValidationError(
                "Enter a local video path, a direct MP4/HLS URL, "
                "or a Google Drive sharing URL."
            )

        if sum(configured_sources) > 1:
            raise ValidationError(
                "Configure only one video source for each movie."
            )

        if self.video_type == self.VIDEO_TYPE_HLS:
            candidate = (self.video_url or "").lower().split("?", 1)[0]
            if self.video_url and not candidate.endswith(".m3u8"):
                raise ValidationError(
                    {"video_url": "HLS video type requires a .m3u8 URL."}
                )

    @property
    def google_drive_file_id(self) -> str:
        if not self.google_drive_url:
            return ""

        url = self.google_drive_url.strip()

        if "/file/d/" in url:
            try:
                return url.split("/file/d/", 1)[1].split("/", 1)[0]
            except IndexError:
                return ""

        parsed = urlparse(url)
        query_id = parse_qs(parsed.query).get("id")
        if query_id:
            return query_id[0]

        return ""

    @property
    def resolved_video_url(self) -> str:
        """
        Return only a genuinely direct remote MP4/HLS URL.

        Google Drive files are streamed through the authenticated Django
        endpoint and are therefore intentionally excluded here.
        """
        return self.video_url.strip() if self.video_url else ""

    @property
    def resolved_video_type(self) -> str:
        if self.video_type != self.VIDEO_TYPE_AUTO:
            return self.video_type

        candidate = self.resolved_video_url.lower().split("?", 1)[0]

        if candidate.endswith(".m3u8"):
            return self.VIDEO_TYPE_HLS

        return self.VIDEO_TYPE_MP4

    @property
    def has_local_video(self) -> bool:
        return bool(self.video_path)

    @property
    def has_remote_video(self) -> bool:
        return bool(self.resolved_video_url)

    @property
    def source_label(self) -> str:
        if self.video_path:
            return "Local video"

        if self.video_url:
            return (
                "HLS stream"
                if self.resolved_video_type == self.VIDEO_TYPE_HLS
                else "Direct MP4"
            )

        if self.google_drive_url:
            return "Google Drive API streaming"

        return "Not configured"

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.title) or "movie"
        candidate = base_slug
        counter = 2

        while Movie.objects.filter(
            slug=candidate
        ).exclude(pk=self.pk).exists():
            candidate = f"{base_slug}-{counter}"
            counter += 1

        return candidate

    def _convert_subtitle_file(self):
        if not self.subtitle:
            return

        subtitle_name = Path(self.subtitle.name).name
        extension = Path(subtitle_name).suffix.lower()

        if extension == ".vtt":
            if self.converted_subtitle.name != self.subtitle.name:
                self.converted_subtitle = self.subtitle
                super().save(update_fields=["converted_subtitle"])
            return

        if extension != ".srt":
            return

        self.subtitle.open("rb")
        raw_content = self.subtitle.read()
        self.subtitle.close()

        decoded_content = None

        for encoding in (
            "utf-8-sig",
            "utf-8",
            "cp1256",
            "windows-1256",
        ):
            try:
                decoded_content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if decoded_content is None:
            decoded_content = raw_content.decode(
                "utf-8",
                errors="replace",
            )

        converted_content = convert_srt_to_vtt(decoded_content)
        converted_name = f"{Path(subtitle_name).stem}.vtt"

        self.converted_subtitle.save(
            converted_name,
            ContentFile(converted_content.encode("utf-8")),
            save=False,
        )

        super().save(update_fields=["converted_subtitle"])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)
        self._convert_subtitle_file()

    def __str__(self):
        return self.title
