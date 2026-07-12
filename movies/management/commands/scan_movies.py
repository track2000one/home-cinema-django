from pathlib import Path

from django.core.management.base import BaseCommand

from movies.models import Movie

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".m4v", ".webm"}


class Command(BaseCommand):
    help = "Add video files from a folder to the movie library"

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str)
        parser.add_argument("--recursive", action="store_true")

    def handle(self, *args, **options):
        folder = Path(options["folder"]).expanduser().resolve()

        if not folder.exists():
            self.stderr.write(self.style.ERROR(f"Folder not found: {folder}"))
            return

        iterator = folder.rglob("*") if options["recursive"] else folder.glob("*")
        added = 0

        for path in iterator:
            if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
                continue

            if Movie.objects.filter(video_path=str(path)).exists():
                continue

            title = path.stem.replace("_", " ").replace(".", " ").strip()
            Movie.objects.create(title=title, video_path=str(path))
            added += 1

        self.stdout.write(self.style.SUCCESS(f"Added {added} movies."))
