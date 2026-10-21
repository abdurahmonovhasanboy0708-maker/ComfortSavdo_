# Python asosiy image
FROM python:3.12-slim

# Terminal chiqishi darhol ko'rinishi uchun
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Pillow uchun kerakli tizim kutubxonalari
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Avval faqat requirements.txt ni nusxalaymiz -- shunda kod o'zgarganda
# Docker keshi tufayli pip install qayta-qayta ishlamaydi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Endi butun loyihani nusxalaymiz
COPY . .

# Static fayllarni yig'ish (CSS/JS/admin statik fayllari)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Production uchun gunicorn bilan ishga tushiramiz
# "comfortsavdo" -- bu sizning settings.py turgan papka nomi
CMD ["gunicorn", "comfortsavdo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]