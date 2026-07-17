from django.urls import path

from . import views


app_name = "series"


urlpatterns = [
    path("", views.series_library, name="library"),
    path("<slug:slug>/", views.series_detail, name="detail"),
    path("<slug:series_slug>/episode/<int:episode_pk>/", views.episode_detail, name="episode"),
    path("drive-stream/<int:episode_pk>/", views.stream_google_drive_episode, name="drive_stream"),
]
