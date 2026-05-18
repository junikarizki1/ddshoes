from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-qjl7*cx^#v*fq8@a3=&vre61typp(moi-c1i7l@(842a2#s(4^')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'jazzmin',  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'store',
    'cart',
    'order',
    'account',
]

JAZZMIN_SETTINGS = {
    # -- Judul & Logo --
    "site_title": "DD Shoes Admin",
    "site_header": "DD Shoes",
    "site_brand": "DD Shoes Store", # Ini yang akan menggantikan tulisan 'Administrasi Django'
    # "site_logo": "img/logodd.png",
    # "login_logo": "images/logodd.png",
    "site_logo_classes": "img-circle",
    "site_icon": None, # Favicon di tab browser
    "welcome_sign": "Selamat Datang di Dashboard DD Shoes",
    "copyright": "DD Shoes Store Pontianak",
    "user_avatar": None, # Bisa diisi 'image' jika model Account punya field foto

    # -- Pencarian --
    "search_model": "my_account.Account",

    # -- Menu Atas --
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Lihat Toko", "url": "/", "new_window": True},
    ],

    # -- Sidebar (Menu Kiri) --
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["store", "order", "my_account", "auth"],

    # -- Ikon (Sangat penting agar dashboard tidak 'jelek') --
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "my_account.Account": "fas fa-user-shield",
        "store.Brand": "fas fa-tag",
        "store.Category": "fas fa-list-ul",
        "store.Product": "fas fa-shoe-prints",
        "store.ProductGallery": "fas fa-images",
        "order.Order": "fas fa-shopping-cart",
        "order.OrderProduct": "fas fa-box-open",
    },
    
    # -- Gaya Form --
    "changeform_format": "horizontal_tabs",
}

# Pengaturan Warna (UI Tweaks) agar dashboard terlihat 'sangar' dan bersih
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary", # Warna brand di sidebar
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light", # Navbar atas putih bersih
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary", # Sidebar gelap biar kontras dan pro
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly", # Tema profesional untuk skripsi
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ddshoes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',
                'store.context_processors.menu_links_brand',
            ],
        },
    },
]

WSGI_APPLICATION = 'ddshoes.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', os.environ.get('DB_NAME', 'ddshoes')),
        'USER': os.environ.get('PGUSER', os.environ.get('DB_USER', 'postgres')),
        'PASSWORD': os.environ.get('PGPASSWORD', os.environ.get('DB_PASSWORD', 'root')),
        'HOST': os.environ.get('PGHOST', os.environ.get('DB_HOST', 'localhost')),
        'PORT': os.environ.get('PGPORT', os.environ.get('DB_PORT', '5432')),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': { 'min_length': 8, }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'id-id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'account.Account'



MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY', 'Mid-client-vWPcASXDMnfQq180')
MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY', 'Mid-server-gaoPXRvg5eN3D9zid5oNEJbk')


#Notifikasi Gmail
# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'tguys894@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'hnxj ysny kdfj dhdw')
DEFAULT_FROM_EMAIL = 'DD Shoes Store'