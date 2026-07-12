import mimetypes
import re
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Movie


RANGE_RE = re.compile(
    r"bytes=(\d+)-(\d*)",
    re.IGNORECASE,
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

    return render(
        request,
        "movies/detail.html",
        {
            "movie": movie,
            "player_source_url": movie.resolved_video_url,
            "player_source_type": movie.resolved_video_type,
        },
    )


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
