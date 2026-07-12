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
        "video_type",
        "genre",
        "year",
    )

    search_fields = (
        "title",
        "description",
        "genre",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

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
                "fields": ("poster",)
            },
        ),
        (
            "Video source",
            {
                "description": (
                    "Configure only one source. For Railway, a direct MP4 "
                    "or HLS URL is recommended. Google Drive is transitional "
                    "and may reject large or heavily viewed files."
                ),
                "fields": (
                    "video_path",
                    "video_url",
                    "video_type",
                    "google_drive_url",
                ),
            },
        ),
        (
            "Subtitle",
            {
                "description": (
                    "Upload SRT or VTT. SRT is converted automatically "
                    "to WebVTT."
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
                "fields": ("created_at",)
            },
        ),
    )

    @admin.display(description="Video source")
    def video_source(self, obj):
        return obj.source_label

    @admin.display(boolean=True, description="Subtitle")
    def has_subtitle(self, obj):
        return bool(obj.converted_subtitle)
