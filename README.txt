طريقة التركيب

1) استبدل الملف:
   movies/templates/movies/detail.html

   بالملف detail.html الموجود هنا.

2) افتح:
   static/css/app.css

   وأضف محتوى app_css_auto_hide.css كاملًا في نهاية الملف.

3) ارفع التعديلات:
   git add .
   git commit -m "Auto hide cinema controls"
   git push

4) بعد نجاح Railway Deployment افتح الصفحة بـ Ctrl + F5.

السلوك:
- أثناء التشغيل تختفي الأدوات بعد 3 ثوانٍ.
- تظهر عند تحريك الفأرة أو لمس الشاشة.
- تبقى ظاهرة عند الإيقاف المؤقت.
- تبقى ظاهرة عند فتح إعدادات الصورة والترجمة.
