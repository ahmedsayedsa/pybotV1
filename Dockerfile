# المرحلة 1: استخدام صورة بايثون رسمية كنقطة بداية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من التخزين المؤقت لـ Docker
COPY requirements.txt .

# تثبيت المتطلبات
# --no-cache-dir لتقليل حجم الصورة
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي كود المشروع إلى مجلد العمل
COPY . .

# تعيين متغير البيئة PORT الذي تستخدمه Cloud Run و Railway
# القيمة الافتراضية 8080 إذا لم يتم توفيرها
ENV PORT 8080

# الأمر النهائي لتشغيل التطبيق باستخدام Gunicorn
# هذا هو الأمر القياسي لتشغيل تطبيقات FastAPI في بيئة الإنتاج
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:$PORT", "app:app"]
