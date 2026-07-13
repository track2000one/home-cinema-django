تم إصلاح المشكلة الفعلية:

1. ملف CSS كان يحتوي عدة نسخ مكررة ومتعارضة من:
   .cinema-stage
   .cinema-controls
   :fullscreen
   controls-hidden

2. JavaScript كان يمنع إخفاء الشريط بعد الضغط على Fullscreen لأن زر
   Fullscreen يظل في حالة hover/focus، فكانت الدالة تعتبر أن الأدوات يجب
   أن تبقى ظاهرة دائمًا.

التركيب:
- استبدل movies/templates/movies/detail.html
- استبدل static/css/app.css بالكامل، ولا تلصق فوق الملف القديم.

ثم:
git add .
git commit -m "Fix fullscreen controls and remove duplicate CSS"
git push
