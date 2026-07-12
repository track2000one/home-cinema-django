from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify


def convert_srt_to_vtt(content: str) -> str:
    """
    Convert basic SRT subtitle content into WebVTT.
    """

    content = content.replace("\r\n", "\n").replace("\r", "\n")

    output_lines = [
        "WEBVTT",
        "",
    ]

    for line in content.split("\n"):
        stripped = line.strip()

        # Remove SRT sequence numbers.
        if stripped.isdigit():
            continue

        # WebVTT uses dots instead of commas in timestamps.
        if "-->" in line:
            line = line.replace(",", ".")

        output_lines.append(line)

    return "\n".join(output_lines).strip() + "\n"


class Movie(models.Model):
    title = models.CharField(
        "Title",
        max_length=220,
    )

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
        help_text=r"Example: E:\Movies\film.mp4",
    )

    google_drive_url = models.URLField(
        "Google Drive URL",
        max_length=1000,
        blank=True,
        help_text=(
            "Paste a Google Drive sharing link, for example: "
            "https://drive.google.com/file/d/FILE_ID/view"
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
        """
        Require either a local video path or a Google Drive URL.
        """

        super().clean()

        if not self.video_path and not self.google_drive_url:
            raise ValidationError(
                "Enter either a local video file path or a Google Drive URL."
            )

    @property
    def google_drive_file_id(self) -> str:
        """
        Extract the Google Drive file ID from common sharing URL formats.
        """

        if not self.google_drive_url:
            return ""

        url = self.google_drive_url.strip()

        # Format:
        # https://drive.google.com/file/d/FILE_ID/view
        if "/file/d/" in url:
            try:
                return url.split("/file/d/", 1)[1].split("/", 1)[0]
            except IndexError:
                return ""

        # Format:
        # https://drive.google.com/open?id=FILE_ID
        if "id=" in url:
            try:
                file_id = url.split("id=", 1)[1]
                return file_id.split("&", 1)[0]
            except IndexError:
                return ""

        # Format:
        # https://drive.google.com/uc?id=FILE_ID
        if "/uc?" in url and "id=" in url:
            try:
                file_id = url.split("id=", 1)[1]
                return file_id.split("&", 1)[0]
            except IndexError:
                return ""

        return ""

    @property
    def google_drive_embed_url(self) -> str:
        """
        Return a Google Drive preview URL suitable for an iframe.
        """

        file_id = self.google_drive_file_id

        if not file_id:
            return ""

        return f"https://drive.google.com/file/d/{file_id}/preview"

    @property
    def has_local_video(self) -> bool:
        return bool(self.video_path)

    @property
    def has_google_drive_video(self) -> bool:
        return bool(self.google_drive_embed_url)

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

                super().save(
                    update_fields=[
                        "converted_subtitle",
                    ]
                )

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

        converted_content = convert_srt_to_vtt(
            decoded_content
        )

        converted_name = (
            f"{Path(subtitle_name).stem}.vtt"
        )

        self.converted_subtitle.save(
            converted_name,
            ContentFile(
                converted_content.encode("utf-8")
            ),
            save=False,
        )

        super().save(
            update_fields=[
                "converted_subtitle",
            ]
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)

        self._convert_subtitle_file()

    def __str__(self):
        return self.title