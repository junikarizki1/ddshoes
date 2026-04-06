import requests
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem 
from .models import Order  # Pastikan model Order sudah dibuat di order/models.py
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse 

# =========================================================
# API KEY KOMERCE ANDA
# =========================================================
KOMERCE_API_KEY = '94obP28b5833ab1b737da714qz6kbIcd' 

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass
        
    if quantity <= 0:
        return redirect('product')
        
    provinces = []
    
    try:
        url = "https://rajaongkir.komerce.id/api/v1/destination/province"
        headers = {
            'key': KOMERCE_API_KEY
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            provinces = data.get('data', []) 
        else:
            print(f"GAGAL Komerce: {response.text}") 
            
    except Exception as e:
        print(f"ERROR SYSTEM: {e}")
        
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'provinces': provinces, 
    }
    
    return render(request, 'order/checkout.html', context)


# =========================================================
# FUNGSI AJAX WILAYAH
# =========================================================
def get_cities(request):
    province_id = request.GET.get('province_id')
    cities = []
    if province_id:
        url = f"https://rajaongkir.komerce.id/api/v1/destination/city/{province_id}"
        headers = {'key': KOMERCE_API_KEY}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cities = data.get('data', [])
        except Exception as e:
            print(f"Error Kota: {e}")
    return JsonResponse({'cities': cities})

def get_districts(request):
    city_id = request.GET.get('city_id')
    districts = []
    if city_id:
        url = f"https://rajaongkir.komerce.id/api/v1/destination/district/{city_id}"
        headers = {'key': KOMERCE_API_KEY}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                districts = response.json().get('data', [])
        except Exception as e:
            print(f"Error Kecamatan: {e}")
    return JsonResponse({'districts': districts})

def get_subdistricts(request):
    district_id = request.GET.get('district_id')
    subdistricts = []
    if district_id:
        url = f"https://rajaongkir.komerce.id/api/v1/destination/sub-district/{district_id}"
        headers = {'key': KOMERCE_API_KEY}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                subdistricts = response.json().get('data', [])
        except Exception as e:
            print(f"Error Kelurahan: {e}")
    return JsonResponse({'subdistricts': subdistricts})

# =========================================================
# FUNGSI AJAX CEK ONGKOS KIRIM
# =========================================================
def get_shipping_cost(request):
    destination = request.GET.get('destination') # ID Kecamatan Tujuan
    weight = request.GET.get('weight', 1000)     # Default 1000 gram (1kg) jika tidak terbaca
    
    # Origin ID Toko Anda 
    origin = '5077' 
    results = []
    
    if destination:
        url = "https://rajaongkir.komerce.id/api/v1/calculate/district/domestic-cost"
        headers = {
            'key': KOMERCE_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Data payload persis seperti dokumentasi cURL Anda
        payload = {
            'origin': origin,
            'destination': destination,
            'weight': weight,
            'courier': 'jne:sicepat:ide:sap:jnt:ninja:tiki:lion:anteraja:pos:ncs:rex:rpx:sentral:star:wahana:dse',
            'price': 'lowest'
        }
        try:
            # Gunakan requests.post karena endpoint ini butuh data (POST)
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])
            else:
                print(f"Error Shipping: {response.text}")
        except Exception as e:
            print(f"Exception Shipping: {e}")
            
    return JsonResponse({'results': results})

# =========================================================
# FUNGSI UNTUK MENYIMPAN PESANAN (PLACE ORDER)
# =========================================================
@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    # 1. Pastikan keranjang tidak kosong
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')

    # 2. Hitung Ulang Total Belanja
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    # 3. Tangkap data dari Form HTML
    if request.method == 'POST':
        # AMBIL ONGKIR YANG DIPILIH DARI DROPDOWN HTML
        try:
            shipping_cost = int(request.POST.get('shipping_cost', 0))
        except ValueError:
            shipping_cost = 0
            
        grand_total = total + shipping_cost
        
        data = Order()
        data.user = current_user
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address = request.POST.get('address')
        
        # Data Wilayah
        data.province_id = request.POST.get('province_id')
        data.province = request.POST.get('province')
        data.city_id = request.POST.get('city_id')
        data.city = request.POST.get('city')
        data.district_id = request.POST.get('district_id')
        data.district = request.POST.get('district')
        data.subdistrict_id = request.POST.get('subdistrict_id')
        data.subdistrict = request.POST.get('subdistrict')
        data.postal_code = request.POST.get('postal_code')
        
        # Simpan nama kurir di catatan order
        courier_service = request.POST.get('courier_service', '')
        user_note = request.POST.get('order_note', '')
        
        if courier_service:
            data.order_note = f"[Kurir: {courier_service}] {user_note}"
        else:
            data.order_note = user_note
        
        # Data Harga
        data.order_total = total
        data.shipping_cost = shipping_cost
        data.grand_total = grand_total
        data.ip = request.META.get('REMOTE_ADDR')
        
        # Simpan ke database tahap 1 (untuk mendapatkan ID barisnya)
        data.save()

        # 4. Generate Nomor Pesanan Unik
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d") 
        
        # Gabungan Tanggal + ID tabel (Contoh: 2026040615)
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        # Alihkan sementara ke home (Nantinya kita alihkan ke halaman pembayaran)
        return redirect('home') 
        
    else:
        return redirect('checkout')


def confirmation(request):
    return render(request, 'order/confirmation.html')