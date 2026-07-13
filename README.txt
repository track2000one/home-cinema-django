تم إصلاح المشكلتين:

1) الاستجابة:
   تم الحفاظ على تنسيقات movie-grid و movie-card الأصلية، وتنظيف CSS المكرر فقط.

2) Fullscreen:
   تم إلغاء Fullscreen على عنصر الفيديو لأنه سبب STATUS_ACCESS_VIOLATION.
   الآن يدخل cinema-stage إلى Fullscreen بشكل آمن، مع إخفاء الأدوات تلقائيًا.

التركيب:
- استبدل movies/templates/movies/detail.html
- استبدل static/css/app.css بالكامل

ثم:
git add .
git commit -m "Fix responsive layout and fullscreen crash"
git push

بعد نجاح Railway:
Ctrl + F5
