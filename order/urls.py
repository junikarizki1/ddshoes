from django.urls import path
from . import views

urlpatterns = [
    # Jalur untuk halaman form checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Jalur rahasia (AJAX) untuk mengambil data kota berdasarkan provinsi
    path('get_cities/', views.get_cities, name='get_cities'),
    
    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_subdistricts/', views.get_subdistricts, name='get_subdistricts'),
    path('get_shipping_cost/', views.get_shipping_cost, name='get_shipping_cost'),
    path('place_order/', views.place_order, name='place_order'),
    
    # Jalur untuk halaman konfirmasi nanti
    path('confirmation/', views.confirmation, name='confirmation'),
]