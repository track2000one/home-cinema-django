GOOGLE DRIVE API STREAMING - INSTALLATION

FILES TO REPLACE
----------------
home_cinema_project/movies/models.py
home_cinema_project/movies/urls.py
home_cinema_project/movies/views.py
home_cinema_project/movies/templates/movies/detail.html
home_cinema_project/home_cinema/settings.py
home_cinema_project/requirements.txt

NO DATABASE MIGRATION IS REQUIRED
---------------------------------
This update changes Python properties and streaming logic only. It does not
add or remove database fields.

GOOGLE CLOUD SETUP
------------------
1. Open Google Cloud Console.
2. Create or select a project.
3. Enable "Google Drive API".
4. Create a Service Account.
5. Open the service account, create a JSON key, and download it once.
6. Copy the service account email address.
7. In Google Drive, share the movies folder with that email as Viewer.
   Existing files inside the shared folder inherit access in normal folders.

RAILWAY VARIABLE
----------------
Create this Railway variable:

GOOGLE_SERVICE_ACCOUNT_JSON

Its value must be the complete JSON content of the downloaded service-account
key, beginning with { and ending with }.

Never upload the JSON key to GitHub.

DEPLOY
------
After pushing the changed files to GitHub, Railway should deploy automatically.

The added packages are:
google-auth>=2.35
requests>=2.32

TEST
----
Open this while logged in:

https://YOUR-DOMAIN/drive-stream/MOVIE_DATABASE_ID/

Expected:
- Status 200 or 206
- Video bytes begin loading
- The normal Google Drive preview page must not appear

If it returns 404:
- The Drive link may be invalid, or
- The file/folder was not shared with the service account.

If it returns 502:
- Google Drive API may not be enabled, or
- The service account lacks access, or
- Google rejected the upstream request.

IMPORTANT LIMITS
----------------
The videos remain stored in Google Drive and do not consume Railway Volume.
However, video traffic passes through Railway, so Railway outbound bandwidth
and Google Drive API/download quotas still apply.
