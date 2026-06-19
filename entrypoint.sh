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

echo "==> Checking database fixtures..."
# Check if any Product exists — if not, load store seed data
PRODUCT_COUNT=$(python manage.py shell -c "from store.models import Product; print(Product.objects.count())" 2>/dev/null || echo "0")
if [ "$PRODUCT_COUNT" = "0" ]; then
    echo "==> No products found — loading store fixtures (categories, brands, products, gallery)..."
    python manage.py loaddata fixtures/seed_store.json
    echo "==> Store fixtures loaded."
else
    echo "==> Products already exist ($PRODUCT_COUNT items) — skipping store fixtures."
fi

# Check if any superuser/admin account exists — if not, load account fixtures
ADMIN_COUNT=$(python manage.py shell -c "from account.models import Account; print(Account.objects.filter(is_superadmin=True).count())" 2>/dev/null || echo "0")
if [ "$ADMIN_COUNT" = "0" ]; then
    echo "==> No admin account found — loading account fixtures..."
    python manage.py loaddata fixtures/seed_superuser.json
    echo "==> Account fixtures loaded."
else
    echo "==> Admin account already exists — skipping account fixtures."
fi

echo "==> Starting Gunicorn..."
exec gunicorn ddshoes.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
