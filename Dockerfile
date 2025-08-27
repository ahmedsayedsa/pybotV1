# 1. استخدم صورة بايثون رسمية كأساس
FROM python:3.11-slim

# 2. قم بتعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. قم بتعيين مجلد العمل داخل الحاوية
WORKDIR /app

# 4. انسخ ملف متطلبات المكتبات أولاً
COPY requirements.txt .

# 5. قم بتثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# 6. انسخ بقية كود التطبيق إلى مجلد العمل
COPY . .

# 7. الأمر الذي سيتم تشغيله عند بدء تشغيل الحاوية
CMD exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app:app
