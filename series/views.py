import json
from functools import lru_cache

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from .models import Episode, Series


DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"


@lru_cache(maxsize=1)
def get_google_drive_session() -> AuthorizedSession:
    raw_json = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not raw_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")
    try:
        service_account_info = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON.") from error
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=[DRIVE_READONLY_SCOPE],
    )
    return AuthorizedSession(credentials)


def google_drive_iterator(upstream_response, chunk_size: int):
    try:
        for chunk in upstream_response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
    finally:
        upstream_response.close()


def copy_stream_headers(source, target):
    for header_name in ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges", "ETag", "Last-Modified"):
        value = source.headers.get(header_name)
        if value:
            target[header_name] = value
    target["Accept-Ranges"] = "bytes"
    target["Cache-Control"] = "private, max-age=3600"
    target["X-Content-Type-Options"] = "nosniff"


@login_required
def series_library(request):
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()
    series_items = Series.objects.prefetch_related("seasons__episodes")
    if query:
        series_items = series_items.filter(title__icontains=query)
    if genre:
        series_items = series_items.filter(genre__iexact=genre)
    genres = Series.objects.exclude(genre="").values_list("genre", flat=True).distinct().order_by("genre")
    return render(request, "series/library.html", {
        "series_items": series_items,
        "genres": genres,
        "query": query,
        "selected_genre": genre,
    })


@login_required
def series_detail(request, slug):
    series = get_object_or_404(Series.objects.prefetch_related("seasons__episodes"), slug=slug)
    return render(request, "series/detail.html", {
        "series": series,
        "seasons": series.seasons.prefetch_related("episodes"),
    })


@login_required
def episode_detail(request, series_slug, episode_pk):
    episode = get_object_or_404(
        Episode.objects.select_related("season", "season__series"),
        pk=episode_pk,
        season__series__slug=series_slug,
    )
    if episode.google_drive_file_id:
        source_url = reverse("series:drive_stream", args=[episode.pk])
        source_type = Episode.VIDEO_TYPE_MP4
    else:
        source_url = episode.video_url
        source_type = episode.resolved_video_type

    season_episodes = episode.season.episodes.all().order_by("number")
    previous_episode = season_episodes.filter(number__lt=episode.number).order_by("-number").first()
    next_episode = season_episodes.filter(number__gt=episode.number).order_by("number").first()

    return render(request, "series/episode.html", {
        "episode": episode,
        "series": episode.season.series,
        "season": episode.season,
        "season_episodes": season_episodes,
        "previous_episode": previous_episode,
        "next_episode": next_episode,
        "player_source_url": source_url,
        "player_source_type": source_type,
    })


@login_required
def stream_google_drive_episode(request, episode_pk):
    episode = get_object_or_404(Episode, pk=episode_pk)
    file_id = episode.google_drive_file_id
    if not file_id:
        raise Http404("This episode has no valid Google Drive file ID.")

    media_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&acknowledgeAbuse=true"
    headers = {"Accept-Encoding": "identity"}
    if request.headers.get("Range"):
        headers["Range"] = request.headers["Range"]

    try:
        upstream = get_google_drive_session().request(
            method="GET",
            url=media_url,
            headers=headers,
            stream=True,
            timeout=(
                int(getattr(settings, "GOOGLE_DRIVE_CONNECT_TIMEOUT", 15)),
                int(getattr(settings, "GOOGLE_DRIVE_READ_TIMEOUT", 120)),
            ),
        )
    except (RuntimeError, requests.RequestException) as error:
        return HttpResponse(
            f"Google Drive streaming is unavailable: {error}",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    if upstream.status_code == 404:
        upstream.close()
        raise Http404("The Google Drive episode file was not found or was not shared with the service account.")
    if upstream.status_code not in (200, 206):
        status_code = upstream.status_code
        upstream.close()
        return HttpResponse(
            f"Google Drive refused the episode request. Upstream status: {status_code}.",
            status=502,
            content_type="text/plain; charset=utf-8",
        )

    response = StreamingHttpResponse(
        google_drive_iterator(
            upstream,
            int(getattr(settings, "GOOGLE_DRIVE_STREAM_CHUNK_SIZE", 1024 * 1024)),
        ),
        status=upstream.status_code,
        content_type=upstream.headers.get("Content-Type") or "video/mp4",
    )
    copy_stream_headers(upstream, response)
    response["Content-Disposition"] = f'inline; filename="episode-{episode.pk}.mp4"'
    return response
