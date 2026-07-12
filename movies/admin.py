from django.contrib import admin

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "year",
        "genre",
        "video_source",
        "has_subtitle",
        "featured",
        "created_at",
    )

    list_filter = (
        "featured",
        "genre",
        "year",
    )

    search_fields = (
        "title",
        "description",
        "genre",
    )

    readonly_fields = (
        "converted_subtitle",
        "created_at",
    )

    fieldsets = (
        (
            "Movie information",
            {
                "fields": (
                    "title",
                    "slug",
                    "year",
                    "genre",
                    "description",
                    "featured",
                )
            },
        ),
        (
            "Poster",
            {
                "fields": (
                    "poster",
                )
            },
        ),
        (
            "Video source",
            {
                "description": (
                    "Enter either a local video path "
                    "or a Google Drive sharing URL."
                ),
                "fields": (
                    "video_path",
                    "google_drive_url",
                ),
            },
        ),
        (
            "Subtitle",
            {
                "description": (
                    "Subtitle files work with local videos. "
                    "SRT files are converted automatically to VTT."
                ),
                "fields": (
                    "subtitle",
                    "converted_subtitle",
                ),
            },
        ),
        (
            "System information",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    @admin.display(
        description="Video source",
    )
    def video_source(self, obj):
        if obj.google_drive_url:
            return "Google Drive"

        if obj.video_path:
            return "Local file"

        return "Not configured"

    @admin.display(
        boolean=True,
        description="Subtitle",
    )
    def has_subtitle(self, obj):
        return bool(obj.converted_subtitle)