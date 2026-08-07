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
    list_display_links = ("title",)
    list_editable = ("featured",)
    list_filter = (
        "featured",
        "video_type",
        "genre",
        "year",
    )
    search_fields = (
        "title",
        "description",
        "genre",
        "video_url",
        "google_drive_url",
    )
    search_help_text = "Search by title, genre, description, or video URL."
    prepopulated_fields = {
        "slug": ("title",),
    }
    readonly_fields = (
        "converted_subtitle",
        "created_at",
    )
    ordering = ("-featured", "-created_at", "title")
    list_per_page = 30
    save_on_top = True
    empty_value_display = "—"

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
                "fields": ("poster",)
            },
        ),
        (
            "Video source",
            {
                "description": (
                    "Configure only one source. For Railway, use a direct MP4 "
                    "or HLS (.m3u8) URL when possible. Google Drive remains "
                    "available for authenticated private streaming."
                ),
                "fields": (
                    "video_type",
                    "video_url",
                    "google_drive_url",
                    "video_path",
                ),
            },
        ),
        (
            "Subtitle",
            {
                "description": (
                    "Upload SRT or VTT. SRT is converted automatically "
                    "to WebVTT for browser playback."
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
                "classes": ("collapse",),
                "fields": ("created_at",),
            },
        ),
    )

    @admin.display(description="Video source")
    def video_source(self, obj):
        return obj.source_label

    @admin.display(boolean=True, description="Subtitle")
    def has_subtitle(self, obj):
        return bool(obj.converted_subtitle)
