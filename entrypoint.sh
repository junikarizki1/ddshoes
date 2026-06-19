#!/bin/sh
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Checking media volume..."
if [ -z "$(find /app/media -mindepth 1 -maxdepth 1 -type d 2>/dev/null)" ]; then
    echo "==> Media volume is empty — seeding from /app/media_seed/ ..."
    cp -rn /app/media_seed/. /app/media/
    echo "==> Seed complete."
else
    echo "==> Media volume already populated — skipping seed."
fi

echo "==> Starting Gunicorn..."
exec gunicorn ddshoes.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
