import requests
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem 

# PASTIKAN OrderProduct DI-IMPORT DI SINI
from .models import Order, OrderProduct 

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse 
import midtransclient
from django.conf import settings

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
        headers = {'key': KOMERCE_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            provinces = data.get('data', []) 
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
# FUNGSI AJAX WILAYAH & ONGKIR
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
                cities = response.json().get('data', [])
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

def get_shipping_cost(request):
    destination = request.GET.get('destination')
    weight = request.GET.get('weight', 1000)
    
    # ID Kecamatan Toko Anda
    origin = '1391' 
    results = []
    
    if destination:
        url = "https://rajaongkir.komerce.id/api/v1/calculate/district/domestic-cost"
        headers = {
            'key': KOMERCE_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'origin': origin,
            'destination': destination,
            'weight': weight,
            'courier': 'jne:sicepat:ide:sap:jnt:ninja:tiki:lion:anteraja:pos:ncs:rex:rpx:sentral:star:wahana:dse',
            'price': 'lowest'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                results = response.json().get('data', [])
        except Exception as e:
            print(f"Exception Shipping: {e}")
            
    return JsonResponse({'results': results})

# =========================================================
# FUNGSI MENYIMPAN PESANAN
# =========================================================
@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if request.method == 'POST':
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
        
        data.province_id = request.POST.get('province_id')
        data.province = request.POST.get('province')
        data.city_id = request.POST.get('city_id')
        data.city = request.POST.get('city')
        data.district_id = request.POST.get('district_id')
        data.district = request.POST.get('district')
        data.subdistrict_id = request.POST.get('subdistrict_id')
        data.subdistrict = request.POST.get('subdistrict')
        data.postal_code = request.POST.get('postal_code')
        
        courier_service = request.POST.get('courier_service', '')
        user_note = request.POST.get('order_note', '')
        
        if courier_service:
            data.order_note = f"[Kurir: {courier_service}] {user_note}"
        else:
            data.order_note = user_note
        
        data.order_total = total
        data.shipping_cost = shipping_cost
        data.grand_total = grand_total
        data.ip = request.META.get('REMOTE_ADDR')
        
        data.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d") 
        
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        # ===========================================================
        # INI DIA SOLUSINYA: PINDAHKAN KERANJANG KE RINCIAN PESANAN
        # ===========================================================
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = data.id           # Hubungkan ke nota Order
            orderproduct.user_id = request.user.id    # Hubungkan ke pembeli
            orderproduct.product_id = item.product_id # Sepatu yang dibeli
            orderproduct.quantity = item.quantity     # Jumlah sepatu
            orderproduct.product_price = item.product.price # Harga saat dibeli
            orderproduct.ordered = True
            orderproduct.save()

            # Opsional: Kurangi stok produk secara otomatis
            product = item.product
            product.stock -= item.quantity
            product.save()
        # ===========================================================

        return redirect('payments', order_number=order_number) 
        
    else:
        return redirect('checkout')

# =========================================================
# FUNGSI MIDTRANS
# =========================================================
@login_required(login_url='login')
def payments(request, order_number):
    try:
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    except ObjectDoesNotExist:
        return redirect('home')

    snap = midtransclient.Snap(
        is_production=False, 
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY
    )

    param = {
        "transaction_details": {
            "order_id": order.order_number,
            "gross_amount": int(order.grand_total) 
        },
        "customer_details": {
            "first_name": order.first_name,
            "last_name": order.last_name,
            "email": order.email,
            "phone": order.phone
        }
    }

    try:
        transaction = snap.create_transaction(param)
        transaction_token = transaction['token']
    except Exception as e:
        print(f"Error Midtrans: {e}")
        transaction_token = ""

    context = {
        'order': order,
        'transaction_token': transaction_token,
        'client_key': settings.MIDTRANS_CLIENT_KEY,
    }
    
    return render(request, 'order/payments.html', context)



@login_required(login_url='login')
def confirmation(request):
    order_number = request.GET.get('order_number')
    
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # Ubah status pesanan menjadi lunas/dibayar HANYA JIKA statusnya masih New
        if order.status == 'New':
            order.status = 'Accepted'
            order.is_ordered = True
            order.save()
            
            # Kosongkan keranjang pembeli HANYA SAAT PERTAMA KALI LUNAS
            CartItem.objects.filter(user=request.user).delete()
        
    except ObjectDoesNotExist:
        return redirect('home')

    context = {
        'order': order,
    }
    
    return render(request, 'order/confirmation.html', context)

# =========================================================
# FUNGSI RIWAYAT PESANAN (BARU)
# =========================================================
@login_required(login_url='login')
def my_orders(request):
    # Ambil semua pesanan milik user ini, urutkan dari yang paling baru
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order/my_orders.html', context)