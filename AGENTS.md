# DD Shoes - AGENTS.md

## Project Overview
Django 5.2 e-commerce store for shoes ("DD Shoes Store Pontianak"). Indonesian locale (`id-id`), timezone `Asia/Jakarta`. Python 3.12, PostgreSQL 16.

## Apps & Architecture
- **account** - Custom user model (`Account`), email-based auth (`USERNAME_FIELD = 'email'`), loyalty system
- **store** - Products, categories, brands, reviews, user interest tracking
- **cart** - Session + user-based cart with `Cart` and `CartItem`
- **order** - Orders, order items, return requests, coupons, Midtrans payment integration
- **ddshoes/** - Project config (settings, urls, wsgi, asgi)

URL routing: `store` at `/`, `cart` at `/cart/`, `order` at `/order/`, `account` at `/account/`, admin at `/admin/`.

## Deployment
- Deployed on **Railway** (see `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` for `*.up.railway.app`)
- `Procfile` → `start.sh`: runs migrations, auto-creates superuser (`admin@gmail.com` / `admin`), collects static, then starts gunicorn
- Gunicorn binds to `$PORT` (default 8000), 2 workers, 2 threads, 120s timeout

## Key Commands
```
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Generate migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests (all empty stubs)
docker compose up                   # Full stack: PostgreSQL 16 + web on :8000
```

## Setup
1. Copy `.env.example` to `.env` and fill in credentials
2. Database env vars: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` (also accepts `PG*` variants)
3. Default dev DB: `ddshoes` / `postgres` / `root` / `localhost:5432`
4. Docker: `docker compose up` (builds from Dockerfile, includes `libcairo2-dev` for xhtml2pdf PDF generation)

## Database
- PostgreSQL, custom user model: `AUTH_USER_MODEL = 'account.Account'`
- `Account` has extra fields: `loyalty_balance` (float), `shoe_size` (int), `is_superadmin`
- `USERNAME_FIELD = 'email'` but model also has a `username` field (required for superuser creation)

## Important Conventions
- `Product.slug` is auto-generated from `product_name` via `slugify()` on every `save()` — manual slugs are overwritten
- `Order.save()` restores stock when status changes to `Cancelled` (reads old status from DB before save)
- `ReturnRequest.save()` sets order status to `Returned` and restores stock when status is `Refunded`
- Order number is generated in `order/views.py` as `YYYYMMDD + order.id` (NOT in signals)
- Loyalty signal (`order/signals.py`): every 200k accumulated from completed orders → auto-generates `LOYAL-XXXXX` coupon (5k discount). Reverses on cancellation.
- `store.signals.update_user_interest()` exists but is NOT wired as a Django signal — called manually from views. `store/apps.py` does not import signals.
- `order/signals.py` IS wired via `order/apps.py` `ready()` — handles `capture_old_status` and `handle_loyalty_logic`
- **Midtrans webhook is commented out** — payment status sync happens via polling in `confirmation()` and `my_orders()` views by calling Midtrans API directly
- **Midtrans runs in sandbox mode** (`is_production=False` in `payments()` view)
- Stock is restored in **multiple places**: `Order.save()`, `ReturnRequest.save()`, `my_orders()` view (Midtrans cancel/expire/deny), and `place_order()` view (decrements on order creation)
- `Order.order_total` stores **net revenue** (product total minus discount), NOT gross total — this is what loyalty calculations use
- Jazzmin `search_model` references `my_account.Account` but the app is named `account` — this is a known quirk that may cause search to fail in admin
- Hardcoded API keys exist in `order/views.py`: `KOMERCE_API_KEY` (RajaOngkir shipping) and binderbyte API key (tracking) — not loaded from env

## External Integrations
- **Midtrans** payment gateway (snap token stored on Order model)
- **Gmail SMTP** for email notifications (shipping confirmations via signal)
- **Ngrok** allowed in `ALLOWED_HOSTS` for tunneling
- **Jazzmin** for customized admin dashboard (theme: flatly, sidebar: dark primary)
- **xhtml2pdf** for PDF invoice generation
- **WhiteNoise** for static file serving in production

## Testing
- All `tests.py` files are empty stubs. No test suite exists.

## Template & Static Structure
- Global templates in `templates/` (base.html, home.html, alerts.html, admin/)
- App-specific templates in `<app>/templates/<app>/`
- Static files: `static/` → collected to `staticfiles/` by WhiteNoise
- Media uploads: `media/photos/` (categories, brands, products, returns, refund_proofs)
- Context processors: `cart_count`, `menu_links_brand`

## Security Notes
- `DEBUG` defaults to `True` via env fallback
- `ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`
- Settings has hardcoded fallback credentials for Midtrans and Gmail — replace before production
