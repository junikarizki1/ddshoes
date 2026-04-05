from django.shortcuts import render, redirect
from .models import Account
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# ==========================================
# 1. FUNGSI LOGIN
# ==========================================
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Cek kecocokan email dan password di database
        user = authenticate(email=email, password=password)

        if user is not None:
            # Jika cocok, masukkan user ke dalam sesi
            auth_login(request, user)
            messages.success(request, 'Anda berhasil login.')
            return redirect('home') # Arahkan kembali ke halaman utama (Home)
        else:
            # Jika salah email atau password
            messages.error(request, 'Email atau password salah! Silakan coba lagi.')
            return redirect('login')

    return render(request, 'account/login.html')

# ==========================================
# 2. FUNGSI REGISTER
# ==========================================
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email ini sudah terdaftar!')
                return redirect('register')
            else:
                username = email.split('@')[0]
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password
                )
                user.phone_number = phone_number
                user.save()
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('login')
        else:
            messages.error(request, 'Password tidak cocok! Silakan coba lagi.')
            return redirect('register')

    return render(request, 'account/register.html')

# ==========================================
# 3. FUNGSI LOGOUT
# ==========================================
def logout(request):
    # Menghapus sesi user yang sedang login
    auth_logout(request)
    # Memunculkan alert sukses logout
    messages.success(request, 'Anda telah berhasil keluar.')
    # Mengarahkan kembali ke halaman login
    return redirect('login')


def tracking(request):
    
    return render(request, 'account/tracking.html')