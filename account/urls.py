from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('tracking/', views.tracking, name='tracking'),
    path('loyalty-program/', views.loyalty_program, name='loyalty_program'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]