HOME CINEMA - DJANGO
====================

Included features:
- Login page
- Movie library
- Search and genre filtering
- Movie details page
- HTML5 video streaming with seek support
- Django admin panel
- Automatic folder scanning
- Local network access
- English-only interface and source text

IMPORTANT
---------
Django cannot run directly from a USB drive connected to a router through FTP.
Run this project on a Windows PC, Mini PC, Raspberry Pi, or NAS.
The movie drive should preferably be connected directly to the server device.

QUICK START
-----------
1. Install Python 3.11 or newer.
2. Enable "Add Python to PATH" during installation.
3. Extract this ZIP file.
4. Run start_server.bat.
5. Run create_admin.bat once.
6. Open:
   http://127.0.0.1:8000

NETWORK ACCESS
--------------
Find the server PC IP address with:

ipconfig

Then open from another device:

http://192.168.1.4:8000

Replace 192.168.1.4 with the actual IPv4 address of the server PC.

ADMIN PANEL
-----------
http://127.0.0.1:8000/admin/

ADDING MOVIES
-------------
Option 1:
Add movies manually from the Django admin panel.

Option 2:
Edit the folder path in scan_movies_example.bat and run it.

Example:
E:\Movies

SECURITY
--------
Use this project only inside your private home network.
Do not forward port 8000 to the public internet.
