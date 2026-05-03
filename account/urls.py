from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('tracking/', views.tracking, name='tracking'),
    path('loyalty-program/', views.loyalty_program, name='loyalty_program'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    # 1. Halaman input email untuk reset
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="account/password_reset.html"), name="reset_password"),
    
    # 2. Pesan bahwa email reset telah dikirim
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="account/password_reset_sent.html"), name="password_reset_done"),
    
    # 3. Link konfirmasi yang diklik dari email
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="account/password_reset_form.html"), name="password_reset_confirm"),
    
    # 4. Pesan bahwa password berhasil diubah
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="account/password_reset_done.html"), name="password_reset_complete"),
]
