from django.urls import path
from . import views

urlpatterns = [
    # Halaman Home
    path('', views.home, name='home'),

    # Halaman Toko Utama
    path('product/', views.product, name='product'),

    # Filter Kategori
    # Nama 'products_by_category' harus ada di sini karena dipanggil oleh models.py
    path('product/category/<slug:category_slug>/', views.product, name='products_by_category'),

    # Detail Produk
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]