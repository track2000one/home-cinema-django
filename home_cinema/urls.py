import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path
from django.utils._os import safe_join


def serve_media(request, path):
    """
    Serve uploaded media files from MEDIA_ROOT.

    Suitable for this small private project.
    For a large public platform, use S3-compatible storage
    or a dedicated media server.
    """

    try:
        file_path = Path(
            safe_join(
                str(settings.MEDIA_ROOT),
                path,
            )
        )
    except Exception as error:
        raise Http404("Invalid media path.") from error

    if not file_path.exists():
        raise Http404("Media file not found.")

    if not file_path.is_file():
        raise Http404("Requested media is not a file.")

    content_type = (
        mimetypes.guess_type(file_path.name)[0]
        or "application/octet-stream"
    )

    response = FileResponse(
        file_path.open("rb"),
        content_type=content_type,
    )

    response["Content-Disposition"] = (
        f'inline; filename="{file_path.name}"'
    )

    return response


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),
    path(
        "media/<path:path>",
        serve_media,
        name="serve_media",
    ),
    path(
        "",
        include("movies.urls"),
    ),
]