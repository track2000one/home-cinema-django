from django.urls import path

from . import views


app_name = "movies"


urlpatterns = [
    path(
        "",
        views.library,
        name="library",
    ),
    path(
        "movie/<str:slug>/",
        views.detail,
        name="detail",
    ),
    path(
        "stream/<int:pk>/",
        views.stream_video,
        name="stream",
    ),
]