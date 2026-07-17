# Home Cinema — Series Feature

## 1. Copy the new app

Copy the complete `series` folder into:

```text
C:\home_cinema_project\series
```

The final path must contain:

```text
C:\home_cinema_project\series\models.py
C:\home_cinema_project\series\admin.py
C:\home_cinema_project\series\templates\series\library.html
```

## 2. Add the app to settings.py

Inside:

```text
C:\home_cinema_project\home_cinema\settings.py
```

Add `"series"` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "movies",
    "series",
]
```

## 3. Add the URL

Inside:

```text
C:\home_cinema_project\home_cinema\urls.py
```

Add this route before the movies route:

```python
path(
    "series/",
    include("series.urls"),
),
```

Example:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("media/<path:path>", serve_media, name="serve_media"),

    path("series/", include("series.urls")),
    path("", include("movies.urls")),
]
```

## 4. Add Series to the main navigation

Inside `templates/base.html`, add:

```html
<a href="{% url 'series:library' %}">Series</a>
```

Place it next to the Home or Movies link.

## 5. Run migrations

```powershell
cd C:\home_cinema_project

python manage.py makemigrations series
python manage.py migrate
python manage.py collectstatic --noinput
```

## 6. Upload to GitHub

```powershell
git add .
git commit -m "Add professional series library"
git push
```

## 7. Add a series and all episode links at once

Open Django Admin:

```text
/admin/
```

Then:

```text
Series
→ Add Series
→ Save and continue editing
→ Bulk import episode links
```

Supported formats:

### One URL per line

```text
https://drive.google.com/file/d/FILE_ID_1/view
https://drive.google.com/file/d/FILE_ID_2/view
https://drive.google.com/file/d/FILE_ID_3/view
```

Choose the default season and starting episode number.

### Title and URL

```text
The Beginning | https://drive.google.com/file/d/FILE_ID_1/view
The Mission | https://drive.google.com/file/d/FILE_ID_2/view
```

### Multiple seasons in one import

```text
S01E01 | The Beginning | https://drive.google.com/file/d/FILE_ID_1/view
S01E02 | The Mission | https://drive.google.com/file/d/FILE_ID_2/view
S02E01 | A New Chapter | https://drive.google.com/file/d/FILE_ID_3/view
```

The importer automatically creates seasons and episodes. Importing the same season and episode number again updates its link instead of creating a duplicate.
