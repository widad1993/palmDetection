# palmDetection — نظام كشف سوسة النخيل (Django)

تطبيق ويب مبني بإطار Django لإدارة المزارع وتحليل الصور/الفيديو لاكتشاف سوسة النخيل باستخدام نموذج محفوظ (`base/ml_models/img_model.pkl`).

## نظرة عامة
- الواجهة: Django + قوالب HTML ضمن `templates/`
- التطبيق: `base/` ويحوي النماذج والعروض وعملية التحليل
- النموذج: ملف `img_model.pkl` يتم تحميله عند بدء التطبيق باستخدام `joblib`
- قاعدة البيانات: SQLite (ملف `db.sqlite3`)
- ملفات ثابتة/وسائط: `static/`, `media/` (الصور تُحفظ تحت `media/images/`)

## متطلبات التشغيل
- Python 3.10 (موصى به)
- نظام Windows أو Linux
- حزم Python الأساسية:
  - Django==4.2.16
  - pillow, numpy, joblib, scikit-learn==1.6.0
  - OpenCV (اختياري لميزات الفيديو/البث): opencv-python (محلي) أو opencv-python-headless (على السيرفر)

> ملاحظة: بعض الحزم في `requirements.txt` ثقيلة وغير مطلوبة للتشغيل الأساسي. استخدم القائمة المصغّرة أدناه عندما تحتاج سرعة وخفة.

## تشغيل محلياً (Windows PowerShell)
1) من جذر المشروع (المجلد الذي يحتوي المجلد الداخلي `palmDetection/`):
```
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install Django==4.2.16 pillow numpy joblib scikit-learn==1.6.0 opencv-python
```
إذا واجهت مشكلة سياسة التنفيذ:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2) تنفيذ الهجرات وإنشاء مستخدم مدير:
```
cd palmDetection
python manage.py migrate
python manage.py createsuperuser
```
(أو إنشاء مدير افتراضي بسرعة):
```
python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin','admin123')"
```

3) التشغيل على المنفذ 9200:
```
python manage.py runserver 0.0.0.0:9200
```
الواجهة: `http://127.0.0.1:9200/` — لوحة الإدارة: `http://127.0.0.1:9200/admin/`

> تشغيل بدون تفعيل البيئة (عند الحاجة):
```
D:\palmDetection\.venv\Scripts\python.exe D:\palmDetection\palmDetection\manage.py runserver 0.0.0.0:9200
```

## إعدادات الأمان المهمة
عدّل `palmDetection/palmDetection/settings.py` عند استخدام نطاق خارجي:
```
ALLOWED_HOSTS = ['your.domain.com', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = [
    'https://your.domain.com',
    'http://your.domain.com',
    'http://127.0.0.1:9200',
    'http://localhost:9200',
    # أنفاق اختيارية:
    'https://*.ngrok-free.app',
    'https://*.trycloudflare.com',
]
```
مهم: لا يقبل CSRF_TRUSTED_ORIGINS القيمة `'*'`؛ يجب تحديد الأصل كاملاً مع البروتوكول.

## حذف تاريخ الصور (تنظيف)
احذف سجلات وصور مزرعة معيّنة (مثلاً رقم 1):
```
python manage.py shell -c "from base.models import FarmHistory; from django.conf import settings; import os, urllib.parse; qs=FarmHistory.objects.filter(farm_id=1); import pathlib; d=0; 
import sys
for fh in list(qs):
    try:
        p=urllib.parse.urlparse(fh.image).path
        rel=p.replace(settings.MEDIA_URL,'').lstrip('/')
        fp=os.path.join(settings.MEDIA_ROOT, rel)
        os.path.exists(fp) and os.remove(fp);
        d+=1
    except Exception as e:
        print('skip', fh.id, e)
qs.delete(); print('deleted files', d)
"
```
أو لمسح الجميع (كل المزارع) عدّل الاستعلام إلى `qs=FarmHistory.objects.all()`.

## نشر على PythonAnywhere (مختصر)
- ارفع المشروع (Zip) وافتحه في مجلدك.
- أنشئ وافعل بيئة:
```
python3.10 -m venv ~/.venvs/palmvenv
source ~/.venvs/palmvenv/bin/activate
pip install --upgrade pip
# متطلبات خفيفة للنشر
cat > ~/requirements-pa.txt << 'EOF'
Django==4.2.16
pillow
numpy
scipy
joblib
scikit-learn==1.6.0
opencv-python-headless
EOF
pip install --no-cache-dir -r ~/requirements-pa.txt
```
- هجرات وتجميع ملفات ثابتة:
```
cd ~/palmDetection   # غيّر المسار حسب موقع manage.py
python manage.py migrate
python manage.py collectstatic --noinput
```
- Web app (Manual, Python 3.10):
  - Virtualenv: `/home/<username>/.venvs/palmvenv`
  - Static: `/static/` → `/home/<username>/palmDetection/staticfiles`
  - WSGI: اجعل `project_path = '/home/<username>/palmDetection'` واضبط `DJANGO_SETTINGS_MODULE='palmDetection.settings'`
  - عدّل في settings: أضف نطاقك في ALLOWED_HOSTS وCSRF_TRUSTED_ORIGINS
  - Reload

> الخطة المجانية قد لا تكفي لتثبيت OpenCV بسبب المساحة. استخدم المدفوع أو عطل ميزات الفيديو.

## نفق للوصول الخارجي من جهازك
- Cloudflare Tunnel (سريع):
```
cloudflared tunnel --url http://127.0.0.1:9200
```
- ngrok:
```
ngrok http http://127.0.0.1:9200 --host-header=rewrite
```
أضف نطاق النفق إلى `CSRF_TRUSTED_ORIGINS` كما في الأعلى.

## مشاكل شائعة وحلول
- 403 CSRF: أضف نطاقك إلى `CSRF_TRUSTED_ORIGINS`، وامسح الكوكيز أو استخدم نافذة خاصة.
- المنفذ 9200 مشغول: استخدم `9201` أو افحص: `netstat -a -n -o | findstr :9200`.
- تفعيل البيئة يفشل على PowerShell: استخدم `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.
- تحذير عدم تطابق scikit-learn عند تحميل النموذج: ثبّت `scikit-learn==1.6.0`.
- PythonAnywhere المجاني: مساحة غير كافية لـ OpenCV؛ استخدم قائمة متطلبات خفيفة أو باقة مدفوعة.

## بنية مهمة في المشروع
- `palmDetection/manage.py` — أوامر Django
- `palmDetection/palmDetection/settings.py` — إعدادات المشروع
- `palmDetection/base/` — النماذج والعروض والمنطق
- `palmDetection/base/ml_models/img_model.pkl` — نموذج التصنيف المحفوظ
- `templates/`, `static/`, `media/` — القوالب والملفات الثابتة والوسائط

---
لأي إعداد خاص (نطاق مخصص، CI/CD، أو مهام تنظيف تلقائي للصور) يمكنك طلب إرشادات إضافية، وسنضبطه حسب بيئتك.
