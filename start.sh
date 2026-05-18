#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell -c "
from account.models import Account
if not Account.objects.filter(is_superadmin=True).exists():
    Account.objects.create_superuser(
        first_name='Admin',
        last_name='DDShoes',
        email='admin@gmail.com',
        username='admin',
        password='admin'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn ddshoes.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
