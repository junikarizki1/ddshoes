# DD Shoes — AGENTS.md

Django 5.2 e-commerce for shoes (Pontianak, Indonesia). Python 3.12, PostgreSQL 16.

## Apps & Entrypoints
- `ddshoes/` — project config, `AUTH_USER_MODEL = 'account.Account'`
- `account/` — custom user (`Account`), email-based auth (`USERNAME_FIELD='email'`), multi-address support
- `store/` — products, categories, brands, reviews, `UserInterest` personalization
- `cart/` — session + user-based cart (`CartItem` linked to `Account`)
- `order/` — orders, items, return requests, coupons, Midtrans payments, invoice PDFs

URLs: `/` store, `/cart/` cart, `/order/` order, `/account/` account, `/admin/` admin.

## Commands
```
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
docker compose up          # Full stack: PostgreSQL 16 + web on :8000
```

No test suite exists (all `tests.py` are empty stubs). No linter/formatter/typecheck config.

## Setup
1. Copy `.env.example` → `.env`, fill in credentials
2. `docker compose up` or set up PostgreSQL manually
3. DB env vars: `DATABASE_URL` (preferred) or `DB_HOST/DB_NAME/DB_USER/DB_PASSWORD/DB_PORT` (also `PG*` variants)
4. Docker includes `libcairo2-dev` (required by xhtml2pdf PDF gen)

## Non-obvious Conventions
- **`Product.slug`** is overwritten on every `save()` via `slugify(product_name)` — manual slugs never stick.
- **`Order.save()`** reads old status from DB first; restores stock if status changes to `Cancelled`.
- **`ReturnRequest.save()`** forces `Order.status='Returned'` and restores stock when status becomes `Refunded`.
- **Order number** is `YYYYMMDD + order.id`, generated inline in `order/views.py:place_order()` (not a signal).
- **`order_total`** stores *net* revenue (product total minus discount), not gross. `grand_total` = net + shipping.
- **Coupon** auto-generation from loyalty: every 200k accumulated from completed orders → `LOYAL-XXXXX` coupon (5k discount). Reversed on cancellation. Defined in `order/signals.py:handle_loyalty_logic`.
- **`update_user_interest`** is duplicated: a standalone copy lives in `store/views.py:227` (the one actually called from `product_detail`), and an identical copy in `store/signals.py` (not wired as a Django signal).
- **`order/signals.py` IS wired** via `order/apps.py.ready()` — handles pre-save status capture and post-save loyalty.
- **Midtrans webhook is commented out** — payment status syncs via polling in `confirmation()` and `my_orders()` views calling Midtrans Core API directly. Sandbox mode (`is_production=False`).
- **Stock restored in 4 places**: `Order.save()`, `ReturnRequest.save()`, `my_orders()` view (Midtrans cancel/expire/deny), and `place_order()` (decrement on creation).
- **Hardcoded API keys** (not loaded from env): `KOMERCE_API_KEY` set independently in both `order/views.py:28` and `account/views.py:13`. Settings also has hardcoded fallback Midtrans/Gmail credentials.
- **Jazzmin `search_model`** references `my_account.Account` but app is named `account` — known quirk, may silently fail in admin search.
- **`MAX_ADDRESSES = 3`** hardcoded in `account/views.py` (enforced in place_order and address management).
- **Shipping cost** uses RajaOngkir via Komerce API; provinces cached in session. Courier tracking URLs stored in `order/templatetags/courier_tags.py`.
- **Custom user model**: `USERNAME_FIELD='email'`, but `username` is still a required field for superuser creation.
- **Context processors**: `cart.context_processors.cart_count` and `store.context_processors.menu_links_brand`.

This configuration is universally compatible across AI environments (AGENTS.md, CLAUDE.md, GEMINI.md).

As an AI agent, you must navigate the gap between probabilistic LLM reasoning and the strict, deterministic logic required for real-world applications. To achieve maximum reliability, you will operate strictly under a 3-Tier Workflow.

The 3-Tier Workflow
Tier 1: The Blueprint (Directives)

Located in the directives/ folder as Markdown files.
These are your standard operating procedures (SOPs). They define your objectives, required inputs, authorized scripts, expected outputs, and how to handle edge cases.
Treat these as clear, natural-language instructions from a human manager.
Tier 2: The Brain (Orchestration)

This is your primary role: intelligent delegation and routing.
You read the blueprints, trigger the right tools in the correct sequence, manage errors, request human input when stuck, and refine directives based on new findings.
You are the bridge. Instead of executing complex tasks (like web scraping) directly, you parse the directive and trigger the corresponding script (e.g., execution/web_scraper.py).
Tier 3: The Muscle (Execution)

Located in the execution/ folder as Python scripts.
These are deterministic, hard-coded tools.
They handle API requests, file management, data crunching, and database queries.
They must be fast, heavily commented, and reliable. All sensitive keys reside in .env.
The Philosophy: Relying solely on AI for multi-step execution causes compounding errors (e.g., 90% accuracy over 5 steps drops to 59% success rate). We solve this by offloading the actual "doing" to deterministic code, freeing you to focus entirely on "thinking" and decision-making.

Core Rules of Engagement
1. Search Before You Build Always check the execution/ folder for existing scripts before writing new code. Avoid redundant tool creation.

2. The Auto-Correction Protocol

When an error occurs, analyze the stack trace immediately.
Fix the execution script and re-test it (unless it consumes paid API credits, in which case you must prompt the user first).
If you hit constraints (e.g., rate limits), adapt the script, test it, and document the solution.
3. Evolve the Blueprints Directives are living documents. Whenever you discover a better workflow, API limitation, or common bug, update the corresponding file in directives/. However, never overwrite or delete a directive entirely without explicit permission. Your instructions must be preserved and improved over time.
