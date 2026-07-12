import json
import mimetypes
import re
from functools import lru_cache
from pathlib import Path

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from .models import Movie


RANGE_RE = re.compile(
    r"bytes=(\d+)-(\d*)",
    re.IGNORECASE,
)

DRIVE_READONLY_SCOPE = (
    "https://www.googleapis.com/auth/drive.readonly"
)


def resolve_local_video_path(raw_path: str) -> Path:
    if not raw_path:
        raise Http404("No local video file is configured.")

    path = Path(raw_path).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / raw_path

    path = path.resolve()

    if not path.exists():
        raise Http404("Video file not found.")

    if not path.is_file():
        raise Http404("The video path is not a file.")

    return path


def video_file_iterator(
    path: Path,
    offset: int,
    length: int,
    chunk_size: int = 1024 * 1024,
):
    with path.open("rb") as video_file:
        video_file.seek(offset)
        remaining = length

        while remaining > 0:
            chunk = video_file.read(min(chunk_size, remaining))

            if not chunk:
                break

            remaining -= len(chunk)
            yield chunk


@lru_cache(maxsize=1)
def get_google_drive_session() -> AuthorizedSession:
    """
    Build and cache an authenticated Google HTTP session.

    GOOGLE_SERVICE_ACCOUNT_JSON must contain the full service-account JSON
    document as a Railway environment variable.
    """
    raw_json = settings.GOOGLE_SERVICE_ACCOUNT_JSON

    if not raw_json:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not configured."
        )

    try:
        service_account_info = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON."
        ) from error

    credentials = (
        service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=[DRIVE_READONLY_SCOPE],
        )
    )

    return AuthorizedSession(credentials)


def google_drive_iterator(upstream_response, chunk_size: int):
    """
    Stream Google Drive bytes and always close the upstream connection.
    """
    try:
        for chunk in upstream_response.iter_content(
            chunk_size=chunk_size
        ):
            if chunk:
                yield chunk
    finally:
        upstream_response.close()


def copy_stream_headers(source, target):
    """
    Forward only headers needed by an HTML5 video element.
    """
    for header_name in (
        "Content-Type",
        "Content-Length",
        "Content-Range",
        "Accept-Ranges",
        "ETag",
        "Last-Modified",
    ):
        value = source.headers.get(header_name)

        if value:
            target[header_name] = value

    target["Accept-Ranges"] = "bytes"
    target["Cache-Control"] = "private, max-age=3600"
    target["X-Content-Type-Options"] = "nosniff"


@login_required
def library(request):
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()
    movies = Movie.objects.all()

    if query:
        movies = movies.filter(title__icontains=query)

    if genre:
        movies = movies.filter(genre__iexact=genre)

    genres = (
        Movie.objects
        .exclude(genre="")
        .values_list("genre", flat=True)
        .distinct()
        .order_by("genre")
    )

    return render(
        request,
        "movies/library.html",
        {
            "movies": movies,
            "genres": genres,
            "query": query,
            "selected_genre": genre,
        },
    )


@login_required
def detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)

    if movie.video_path:
        player_source_url = reverse(
            "movies:stream",
            args=[movie.pk],
        )
        player_source_type = Movie.VIDEO_TYPE_MP4

    elif movie.google_drive_file_id:
        player_source_url = reverse(
            "movies:drive_stream",
            args=[movie.pk],
        )
        player_source_type = Movie.VIDEO_TYPE_MP4

    else:
        player_source_url = movie.resolved_video_url
        player_source_type = movie.resolved_video_type

    return render(
        request,
        "movies/detail.html",
        {
            "movie": movie,
            "player_source_url": player_source_url,
            "player_source_type": player_source_type,
        },
    )


@login_required
def stream_google_drive_video(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    file_id = movie.google_drive_file_id

    if not file_id:
        raise Http404(
            "This movie has no valid Google Drive file ID."
        )

    media_url = (
        "https://www.googleapis.com/drive/v3/files/"
        f"{file_id}?alt=media&acknowledgeAbuse=true"
    )

    upstream_headers = {}

    range_header = request.headers.get("Range")
    if range_header:
        upstream_headers["Range"] = range_header

    # Helps Google return a browser-playable response.
    upstream_headers["Accept-Encoding"] = "identity"

    try:
        session = get_google_drive_session()
        upstream = session.request(
            method="GET",
            url=media_url,
            headers=upstream_headers,
            stream=True,
            timeout=(
                settings.GOOGLE_DRIVE_CONNECT_TIMEOUT,
                settings.GOOGLE_DRIVE_READ_TIMEOUT,
            ),
        )
    except (
        RuntimeError,
        requests.RequestException,
    ) as error:
        return HttpResponse(
            f"Google Drive streaming is unavailable: {error}",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    if upstream.status_code == 404:
        upstream.close()
        raise Http404(
            "The Google Drive file was not found or was not shared "
            "with the service account."
        )

    if upstream.status_code not in (200, 206):
        status_code = upstream.status_code
        upstream.close()

        return HttpResponse(
            (
                "Google Drive refused the video request. "
                f"Upstream status: {status_code}. "
                "Check Drive API access and folder sharing."
            ),
            status=502,
            content_type="text/plain; charset=utf-8",
        )

    content_type = (
        upstream.headers.get("Content-Type")
        or "video/mp4"
    )

    if request.method == "HEAD":
        response = HttpResponse(
            status=upstream.status_code,
            content_type=content_type,
        )
        copy_stream_headers(upstream, response)
        upstream.close()
        return response

    response = StreamingHttpResponse(
        google_drive_iterator(
            upstream,
            settings.GOOGLE_DRIVE_STREAM_CHUNK_SIZE,
        ),
        status=upstream.status_code,
        content_type=content_type,
    )

    copy_stream_headers(upstream, response)

    safe_filename = (
        Path(movie.title).name.replace('"', "")
        or f"movie-{movie.pk}"
    )
    response["Content-Disposition"] = (
        f'inline; filename="{safe_filename}.mp4"'
    )

    return response


@login_required
def stream_video(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    if not movie.video_path:
        raise Http404("This movie has no local video file.")

    path = resolve_local_video_path(movie.video_path)
    file_size = path.stat().st_size

    content_type = (
        mimetypes.guess_type(path.name)[0]
        or "application/octet-stream"
    )

    range_header = request.headers.get("Range")

    if range_header:
        match = RANGE_RE.match(range_header)

        if not match:
            raise Http404("Invalid byte range.")

        start = int(match.group(1))
        end_text = match.group(2)
        end = int(end_text) if end_text else file_size - 1
        end = min(end, file_size - 1)

        if start >= file_size or start > end:
            raise Http404("Invalid byte range.")

        length = end - start + 1

        response = StreamingHttpResponse(
            video_file_iterator(path, start, length),
            status=206,
            content_type=content_type,
        )

        response["Content-Length"] = str(length)
        response["Content-Range"] = (
            f"bytes {start}-{end}/{file_size}"
        )
    else:
        response = FileResponse(
            path.open("rb"),
            content_type=content_type,
        )
        response["Content-Length"] = str(file_size)

    response["Accept-Ranges"] = "bytes"
    response["Content-Disposition"] = (
        f'inline; filename="{path.name}"'
    )
    response["Cache-Control"] = "private, max-age=3600"

    return response
