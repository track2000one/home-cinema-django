# Series feature

The new `series` Django app adds:

- Professional series library
- Seasons and episodes
- Google Drive API episode streaming
- MP4 and HLS support
- Subtitle support
- Bulk episode-link import from Django Admin

After merging and deployment, run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Open `/admin/`, create a Series, save it, then use **Bulk import episode links**.

Supported formats:

```text
https://drive.google.com/file/d/FILE_ID/view
Episode title | https://drive.google.com/file/d/FILE_ID/view
S01E01 | Episode title | https://drive.google.com/file/d/FILE_ID/view
```
