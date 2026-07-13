الحل النهائي:

- زر Fullscreen يدخل عنصر الفيديو نفسه إلى ملء الشاشة.
- شريط الموقع المخصص لا يدخل إلى ملء الشاشة نهائيًا.
- المتصفح يعرض أدوات الفيديو الأصلية ثم يخفيها تلقائيًا.
- يعمل على الكمبيوتر والجوال والآيباد.
- تم تنظيف app.css من جميع نسخ المشغل المكررة والمتعارضة.

استبدل بالكامل:
1. movies/templates/movies/detail.html
2. static/css/app.css

ثم:
git add .
git commit -m "Use native video fullscreen"
git push
