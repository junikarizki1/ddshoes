from django.urls import path
from . import views

urlpatterns = [
    # Jalur untuk halaman form checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Rangkaian AJAX untuk mengambil wilayah dari Komerce
    path('get_cities/', views.get_cities, name='get_cities'),
    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_subdistricts/', views.get_subdistricts, name='get_subdistricts'),
    
    # Jalur AJAX untuk menghitung ongkos kirim dinamis
    path('get_shipping_cost/', views.get_shipping_cost, name='get_shipping_cost'),
    
    # Jalur untuk menyimpan pesanan
    path('place_order/', views.place_order, name='place_order'),
    
    # ==========================================
    # INI JALUR YANG HILANG (HALAMAN PEMBAYARAN)
    # ==========================================
    path('payments/<str:order_number>/', views.payments, name='payments'),
    
    # Jalur untuk halaman konfirmasi
    path('confirmation/', views.confirmation, name='confirmation'),
    
    path('my_orders/', views.my_orders, name='my_orders'),
    
    path('midtrans-webhook/', views.midtrans_webhook, name='midtrans_webhook'),
    path('track/', views.track_order, name='track_order'),
    path('admin_invoice_pdf/<int:order_id>/', views.admin_order_pdf, name='admin_order_pdf'),
    path('submit_return/<int:order_id>/', views.submit_return, name='submit_return'),
]