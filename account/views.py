from django.shortcuts import render, redirect
from .models import Account
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from order.models import Coupon

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
        shoe_size = request.POST.get('shoe_size') 

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

                if shoe_size and shoe_size.strip():
                    user.shoe_size = int(shoe_size)
                
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


# ==========================================
# 4. FUNGSI TRACKING
# ==========================================
def tracking(request):
    
    return render(request, 'account/tracking.html')


# ==========================================
# 5. FUNGSI LOYALTY
# ==========================================
@login_required(login_url='login')
def loyalty_program(request):
    # Ambil semua kupon milik user yang belum dipakai
    coupons = Coupon.objects.filter(user=request.user, is_used=False).order_by('-id')
    
    target_voucher = 200000
    current_balance = request.user.loyalty_balance
    
    # Hitung sisa belanja untuk ditampilkan di halaman
    sisa_belanja = target_voucher - current_balance
    if sisa_belanja < 0: sisa_belanja = 0

    context = {
        'coupons': coupons,
        'sisa_belanja': sisa_belanja,
        'target_voucher': target_voucher,
    }
    return render(request, 'account/loyalty_program.html', context)


# ==========================================
# 5. FUNGSI EDIT PROFILE
# ==========================================
@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        # Ambil data dari form
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        
        # Update shoe_size (Penting untuk algoritma rekomendasi)
        new_size = request.POST.get('shoe_size')
        if new_size:
            user.shoe_size = int(new_size)
        
        user.save()
        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('edit_profile')

    return render(request, 'account/edit_profile.html', {'user': user})