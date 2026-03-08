from django.urls import path
from . import views

urlpatterns = [
    # Akses ke /order/checkout/ akan memanggil fungsi checkout dengan nama url 'checkout'
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
]