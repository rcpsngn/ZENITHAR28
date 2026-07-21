#!/bin/sh
set -e

echo ">> Veritabanı migration'ları uygulanıyor..."
python manage.py migrate --noinput

echo ">> Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput

echo ">> Gunicorn başlatılıyor..."
exec gunicorn zenithar.wsgi:application --bind 0.0.0.0:8000 --workers 3
