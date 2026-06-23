from django.shortcuts import render, redirect, get_object_or_404
from .models import Account, Address
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from order.models import Coupon
import requests
import base64
from django.core.files.base import ContentFile
import io
from django.conf import settings

KOMERCE_API_KEY = settings.KOMERCE_API_KEY
MAX_ADDRESSES = 3

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
        form = RegistrationForm(request.POST)
        
        # Jika form.is_valid() bernilai False (karena password "1234"), 
        # maka blok kode di bawah ini TIDAK AKAN dijalankan.
        if form.is_valid():
            # Mengambil data yang SUDAH divalidasi
            data = form.cleaned_data
            
            user = Account.objects.create_user(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                username=data['email'].split('@')[0],
                password=data['password']
            )
            user.phone_number = data['phone_number']
            user.shoe_size = data['shoe_size']
            user.save()

            messages.success(request, 'Registrasi berhasil!')
            return redirect('login')
        else:
            # Jika gagal (password 1234), kirim pesan error ke user
            messages.error(request, 'Pendaftaran gagal. Perhatikan ketentuan keamanan kata sandi.')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})

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
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        
        new_size = request.POST.get('shoe_size')
        if new_size:
            user.shoe_size = int(new_size)
        
        if request.POST.get('remove_photo') == '1':
            if user.profile_photo:
                user.profile_photo.delete(save=False)
            user.profile_photo = None
        else:
            cropped_data = request.POST.get('profile_photo_cropped')
            if cropped_data and cropped_data.startswith('data:image'):
                # Jalur utama: hasil crop dari Cropper.js (base64)
                header, imgstr = cropped_data.split(';base64,')
                ext = header.split('/')[-1]
                if ext.lower() == 'jpeg':
                    ext = 'jpg'
                img_data = base64.b64decode(imgstr)
                # Hapus foto lama dulu sebelum simpan yang baru
                if user.profile_photo:
                    user.profile_photo.delete(save=False)
                user.profile_photo.save(
                    f'profile_{user.id}.{ext}',
                    ContentFile(img_data),
                    save=False
                )
            elif 'profile_photo' in request.FILES:
                # Jalur fallback: file langsung tanpa crop
                if user.profile_photo:
                    user.profile_photo.delete(save=False)
                user.profile_photo = request.FILES['profile_photo']
        
        user.save()
        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('edit_profile')

    return render(request, 'account/edit_profile.html', {'user': user})


# ==========================================
# 6. ADDRESS MANAGEMENT
# ==========================================
@login_required(login_url='login')
def address_list(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'account/address_list.html', {'addresses': addresses})


@login_required(login_url='login')
def add_address(request):
    if Address.objects.filter(user=request.user).count() >= MAX_ADDRESSES:
        messages.error(request, f'Maksimal {MAX_ADDRESSES} alamat tersimpan. Hapus alamat lama untuk menambah baru.')
        return redirect('address_list')

    provinces = []
    try:
        url = "https://rajaongkir.komerce.id/api/v1/destination/province"
        headers = {'key': KOMERCE_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            provinces = response.json().get('data', [])
    except Exception:
        pass

    if request.method == 'POST':
        address = Address.objects.create(
            user=request.user,
            label=request.POST.get('label', 'Alamat Baru'),
            province_id=request.POST.get('province_id'),
            province_name=request.POST.get('province'),
            city_id=request.POST.get('city_id'),
            city_name=request.POST.get('city'),
            district_id=request.POST.get('district_id'),
            district_name=request.POST.get('district'),
            subdistrict_id=request.POST.get('subdistrict_id'),
            subdistrict_name=request.POST.get('subdistrict'),
            postal_code=request.POST.get('postal_code'),
            address=request.POST.get('address'),
            shipping_service=request.POST.get('shipping_service', ''),
            shipping_cost=float(request.POST.get('shipping_cost', 0)),
        )
        messages.success(request, 'Alamat berhasil ditambahkan!')
        return redirect('address_list')

    return render(request, 'account/address_form.html', {
        'provinces': provinces,
        'title': 'Tambah Alamat Baru',
        'is_edit': False,
    })


@login_required(login_url='login')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    provinces = []
    try:
        url = "https://rajaongkir.komerce.id/api/v1/destination/province"
        headers = {'key': KOMERCE_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            provinces = response.json().get('data', [])
    except Exception:
        pass

    if request.method == 'POST':
        address.label = request.POST.get('label', 'Alamat Baru')
        address.province_id = request.POST.get('province_id')
        address.province_name = request.POST.get('province')
        address.city_id = request.POST.get('city_id')
        address.city_name = request.POST.get('city')
        address.district_id = request.POST.get('district_id')
        address.district_name = request.POST.get('district')
        address.subdistrict_id = request.POST.get('subdistrict_id')
        address.subdistrict_name = request.POST.get('subdistrict')
        address.postal_code = request.POST.get('postal_code')
        address.address = request.POST.get('address')
        address.shipping_service = request.POST.get('shipping_service', '')
        address.shipping_cost = float(request.POST.get('shipping_cost', 0))
        address.save()
        messages.success(request, 'Alamat berhasil diperbarui!')
        return redirect('address_list')

    return render(request, 'account/address_form.html', {
        'provinces': provinces,
        'address': address,
        'title': 'Edit Alamat',
        'is_edit': True,
    })


@login_required(login_url='login')
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Alamat berhasil dihapus.')
    return redirect('address_list')


@login_required(login_url='login')
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, 'Alamat default berhasil diubah.')
    return redirect('address_list')