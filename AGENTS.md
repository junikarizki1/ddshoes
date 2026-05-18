# DD Shoes - AGENTS.md

## Project Overview
Django e-commerce store for shoes ("DD Shoes Store Pontianak"). Indonesian locale (`id-id`), timezone `Asia/Jakarta`.

## Apps & Architecture
- **account** - Custom user model (`Account`), email-based auth (`USERNAME_FIELD = 'email'`), loyalty system
- **store** - Products, categories, brands, reviews, user interest tracking
- **cart** - Session + user-based cart with `Cart` and `CartItem`
- **order** - Orders, order items, return requests, coupons, Midtrans payment integration
- **ddshoes/** - Project config (settings, urls, wsgi, asgi)

## Key Commands
```
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Generate migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests (all empty stubs)
```

## Database
- PostgreSQL, database `ddshoes`, user `postgres`, password `root`, port `5432`
- Custom user model: `AUTH_USER_MODEL = 'account.Account'`

## Important Conventions
- `Product.slug` is auto-generated from `product_name` on every save (overrides manual slugs)
- `Order.save()` restores stock when status changes to `Cancelled`
- `ReturnRequest.save()` sets order status to `Returned` and restores stock when `Refunded`
- Loyalty: 200k balance → auto-generates `LOYAL-XXXXX` coupon (5k discount)
- Signals in `order/signals.py` handle order number generation and loyalty point logic
- User interest tracking via `store.signals.update_user_interest()` (called from views, not wired to signals)

## External Integrations
- **Midtrans** payment gateway (keys in settings.py)
- **Gmail SMTP** for email notifications (credentials in settings.py)
- **Ngrok** allowed in `ALLOWED_HOSTS` for tunneling
- **Jazzmin** for customized admin dashboard

## Testing
- All `tests.py` files are empty stubs. No test suite exists yet.

## Security Notes
- `DEBUG = True`, `ALLOWED_HOSTS = ['*']` (overridden later with specific hosts)
- Secret keys, Midtrans credentials, and Gmail app password are hardcoded in `settings.py`

## Template Structure
- Global templates in `templates/` (base.html, home.html, alerts.html, admin/)
- App-specific templates in `<app>/templates/<app>/`

## Static/Media
- Static files: `static/` directory
- Media uploads: `media/` directory (`photos/categories`, `photos/brands`, `photos/products`, etc.)
