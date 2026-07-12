from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=220, verbose_name="Title")),
                ("slug", models.SlugField(blank=True, max_length=240, unique=True)),
                ("year", models.PositiveIntegerField(blank=True, null=True, verbose_name="Year")),
                ("genre", models.CharField(blank=True, max_length=120, verbose_name="Genre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("poster", models.ImageField(blank=True, null=True, upload_to="posters/", verbose_name="Poster")),
                ("video_path", models.CharField(help_text="Example: E:\\Movies\\film.mp4", max_length=1000, verbose_name="Video file path")),
                ("featured", models.BooleanField(default=False, verbose_name="Featured")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-featured", "-created_at", "title"]},
        ),
    ]
