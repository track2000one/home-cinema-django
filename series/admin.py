from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse

from .forms import BulkEpisodeImportForm
from .models import Episode, Season, Series


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ("number", "title")
    show_change_link = True


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "genre", "season_count", "episode_total", "featured")
    list_filter = ("featured", "genre", "year")
    search_fields = ("title", "description", "genre")
    readonly_fields = ("created_at",)
    inlines = [SeasonInline]
    change_form_template = "admin/series/series/change_form.html"

    @admin.display(description="Seasons")
    def season_count(self, obj):
        return obj.seasons.count()

    @admin.display(description="Episodes")
    def episode_total(self, obj):
        return obj.episode_count

    def get_urls(self):
        return [
            path(
                "<int:series_id>/import-episodes/",
                self.admin_site.admin_view(self.import_episodes_view),
                name="series_series_import_episodes",
            ),
        ] + super().get_urls()

    def import_episodes_view(self, request, series_id):
        series = get_object_or_404(Series, pk=series_id)
        form = BulkEpisodeImportForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            try:
                rows = form.parse_lines()
            except Exception as error:
                form.add_error(None, error)
            else:
                created_count = 0
                updated_count = 0
                for row in rows:
                    season, _ = Season.objects.get_or_create(
                        series=series,
                        number=row["season_number"],
                        defaults={"title": f"Season {row['season_number']}"},
                    )
                    _, created = Episode.objects.update_or_create(
                        season=season,
                        number=row["episode_number"],
                        defaults={
                            "title": row["title"] or f"Episode {row['episode_number']}",
                            "google_drive_url": row["url"],
                            "video_url": "",
                            "video_type": Episode.VIDEO_TYPE_MP4,
                        },
                    )
                    created_count += int(created)
                    updated_count += int(not created)

                self.message_user(
                    request,
                    f"Import completed: {created_count} created, {updated_count} updated.",
                    level=messages.SUCCESS,
                )
                return redirect(reverse("admin:series_series_change", args=[series.pk]))

        context = {
            **self.admin_site.each_context(request),
            "title": f"Bulk import episodes — {series.title}",
            "series": series,
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/series/series/import_episodes.html", context)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("series", "number", "title", "episode_count")
    list_filter = ("series",)
    search_fields = ("series__title", "title")

    @admin.display(description="Episodes")
    def episode_count(self, obj):
        return obj.episodes.count()


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("series_title", "season_number", "number", "title", "video_source", "has_subtitle")
    list_filter = ("season__series", "season__number", "video_type")
    search_fields = ("season__series__title", "title", "description")
    readonly_fields = ("slug", "converted_subtitle", "created_at")

    @admin.display(description="Series")
    def series_title(self, obj):
        return obj.season.series.title

    @admin.display(description="Season")
    def season_number(self, obj):
        return obj.season.number

    @admin.display(description="Video source")
    def video_source(self, obj):
        return obj.source_label

    @admin.display(boolean=True, description="Subtitle")
    def has_subtitle(self, obj):
        return bool(obj.converted_subtitle)
