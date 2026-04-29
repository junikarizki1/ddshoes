import requests
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import CartItem 
from .models import Order, OrderProduct, Coupon
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse 
import midtransclient
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa # Library untuk convert HTML ke PDF
from django.shortcuts import redirect
from django.contrib import messages
from .forms import ReturnRequestForm
import uuid



# =========================================================
# API KEY KOMERCE ANDA
# =========================================================
KOMERCE_API_KEY = '94obP28b5833ab1b737da714qz6kbIcd' 

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += float(cart_item.product.price * cart_item.quantity)
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
        return redirect('home')

    # 1. Hitung Total Belanja dengan Aman
    for cart_item in cart_items:
        total += float(cart_item.product.price) * cart_item.quantity
        quantity += cart_item.quantity

    if request.method == 'POST':
        # 2. Ambil Ongkir & Diskon
        try:
            shipping_cost = float(request.POST.get('shipping_cost', 0))
        except (ValueError, TypeError):
            shipping_cost = 0.0
            
        discount = float(request.session.get('discount_amount', 0))
        
        # 3. Kalkulasi Grand Total
        grand_total = float(total) + float(shipping_cost) - float(discount)
        
        # 4. Simpan Data Order
        data = Order()
        data.user = current_user
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address = request.POST.get('address')
        data.province = request.POST.get('province')
        data.city = request.POST.get('city')
        data.district = request.POST.get('district')
        data.subdistrict = request.POST.get('subdistrict')
        data.postal_code = request.POST.get('postal_code')
        
        data.order_total = total
        data.shipping_cost = shipping_cost
        data.grand_total = grand_total
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        # 5. Generate Order Number
        current_date = datetime.date.today().strftime("%Y%m%d") 
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        # --- TAMBAHAN: LOGIKA PENGUNCIAN VOUCHER (AGAR TIDAK DOUBLE PAKAI) ---
        used_coupon_id = request.session.get('coupon_id')
        if used_coupon_id:
            try:
                from order.models import Coupon # Pastikan import sudah ada di atas
                voucher = Coupon.objects.get(id=used_coupon_id, user=current_user)
                voucher.is_used = True
                voucher.save()
            except Coupon.DoesNotExist:
                pass
        # --------------------------------------------------------------------

        # 6. Pindahkan Item ke OrderProduct
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = data.id
            orderproduct.user_id = current_user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = float(item.product.price)
            orderproduct.ordered = True
            orderproduct.save()

            # Stok dikurangi
            product = item.product
            product.stock -= int(item.quantity)
            product.save()

        # 7. Bersihkan Sesi & Keranjang
        cart_items.delete()
        
        # Bersihkan semua session terkait diskon
        if 'discount_amount' in request.session:
            del request.session['discount_amount']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        if 'coupon_code' in request.session:
            del request.session['coupon_code']

        return redirect('payments', order_number=order_number) 
    
    return redirect('checkout')

# =========================================================
# FUNGSI HALAMAN PEMBAYARAN MIDTRANS
# =========================================================
@login_required(login_url='login')
def payments(request, order_number):
    try:
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
        order_products = OrderProduct.objects.filter(order=order)
    except Order.DoesNotExist:
        return redirect('home')

    snap = midtransclient.Snap(
        is_production=False,
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY
    )

    item_list = []
    # 1. Tambahkan Produk
    for item in order_products:
        item_list.append({
            "id": f"PROD-{item.product.id}",
            "price": int(float(item.product_price)), # Bungkus float sebelum int
            "quantity": item.quantity,
            "name": item.product.product_name[:30]
        })

    # 2. Tambahkan Ongkir
    item_list.append({
        "id": "SHIPPING",
        "price": int(float(order.shipping_cost)), # Bungkus float sebelum int
        "quantity": 1,
        "name": "Ongkos Kirim"
    })

    # 3. PERBAIKAN LOGIKA DISKON (Penyebab Error)
    # Gunakan float() untuk semua variabel agar bisa dikalkulasi
    total_normal = sum(float(item.product_price) * item.quantity for item in order_products) + float(order.shipping_cost)
    discount_amount = total_normal - float(order.grand_total)

    if discount_amount > 1: # Gunakan toleransi > 1 rupiah
        item_list.append({
            "id": "DISCOUNT-LOYALTY",
            "price": -int(discount_amount), 
            "quantity": 1,
            "name": "Potongan Voucher"
        })

    param = {
        "transaction_details": {
            "order_id": order.order_number,
            "gross_amount": int(float(order.grand_total)) # Bungkus float
        },
        "item_details": item_list,
        "customer_details": {
            "first_name": order.first_name,
            "last_name": order.last_name,
            "email": request.user.email,
            "phone": order.phone
        }
    }
    
    try:
        snap_transaction = snap.create_transaction(param)
        snap_token = snap_transaction['token']
        order.snap_token = snap_token
        order.save()
    except Exception as e:
        print(f"Error Midtrans: {e}")
        snap_token = None

    context = {
        'order': order,
        'snap_token': snap_token,
        'client_key': settings.MIDTRANS_CLIENT_KEY,
    }
    return render(request, 'order/payments.html', context)



# =========================================================
# FUNGSI KONFIRMASI PESANAN (DIPERBARUI)
# =========================================================
@login_required(login_url='login')
def confirmation(request):
    order_number = request.GET.get('order_number')
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # --- PERBAIKAN DI SINI ---
        # Jika status sudah 'Cancelled' atau 'Completed', BERHENTI DI SINI.
        # Jangan tanya Midtrans, jangan jalankan kode di bawahnya. 
        # Ini menghormati keputusan Admin.
        if order.status in ['Cancelled', 'Completed', 'Returned']:
            context = {'order': order}
            return render(request, 'order/confirmation.html', context)
        # -------------------------

        # Jika lolos dari cek di atas (berarti status masih New/Pending/Accepted),
        # baru kita sinkronkan dengan Midtrans.
        core_api = midtransclient.CoreApi(
            is_production=False,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )

        try:
            response = core_api.transactions.status(order.order_number)
            transaction_status = response.get('transaction_status')
            
            # Update database berdasarkan Midtrans
            if transaction_status in ['capture', 'settlement']:
                order.status = 'Accepted'
                order.is_ordered = True
            elif transaction_status in ['cancel', 'expire', 'deny']:
                # Jika Midtrans bilang batal, kita ikuti
                order.status = 'Cancelled'
                order.is_ordered = False
            
            order.save()
        except Exception as e:
            print(f"Midtrans Sync Error: {e}")

    except ObjectDoesNotExist:
        return redirect('home')

    context = {'order': order}
    return render(request, 'order/confirmation.html', context)

# =========================================================
# FUNGSI RIWAYAT PESANAN (DENGAN AUTO-SYNC STOK MIDTRANS)
# =========================================================
@login_required(login_url='login')
def my_orders(request):
    # Ambil semua pesanan milik user ini
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Siapkan alat untuk bertanya ke server Midtrans
    core_api = midtransclient.CoreApi(
        is_production=False,
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY
    )

    # Lakukan pengecekan untuk setiap pesanan yang statusnya belum lunas
    for order in orders:
        if order.status in ['New', 'Pending'] and not order.is_ordered:
            try:
                # Tanya status terbarunya ke Midtrans
                response = core_api.transactions.status(order.order_number)
                transaction_status = response.get('transaction_status')

                # Jika Midtrans bilang pesanan ini dibatalkan atau sudah kadaluarsa
                if transaction_status in ['cancel', 'expire', 'deny']:
                    
                    # 1. Batalkan pesanan di database kita
                    order.status = 'Cancelled'
                    order.is_ordered = False
                    order.save()
                    
                    # 2. KEMBALIKAN STOK SEPATU KE ETALASE!
                    order_products = OrderProduct.objects.filter(order=order)
                    for item in order_products:
                        product = item.product
                        product.stock += item.quantity
                        product.save()
                        
            except Exception as e:
                # Jika error (misalnya pesanan belum sempat terekam di Midtrans), lewati saja
                pass

    context = {
        'orders': orders,
    }
    return render(request, 'order/my_orders.html', context)


# =========================================================
# FUNGSI WEBHOOK MIDTRANS (OTOMATISASI STATUS PEMBAYARAN)
# # =========================================================
# @csrf_exempt
# def midtrans_webhook(request):
#     if request.method == 'POST':
#         try:
#             # 1. Tangkap surat/data JSON yang dikirim oleh Midtrans
#             data = json.loads(request.body)
#             order_id = data.get('order_id')
#             transaction_status = data.get('transaction_status')
#             fraud_status = data.get('fraud_status')

#             # 2. Cari pesanan tersebut di database kita
#             try:
#                 order = Order.objects.get(order_number=order_id)
#             except ObjectDoesNotExist:
#                 return HttpResponse('Pesanan tidak ditemukan', status=404)

#             # 3. Ubah status pesanan berdasarkan laporan Midtrans
#             if transaction_status == 'capture':
#                 if fraud_status == 'challenge':
#                     order.status = 'Pending'
#                 elif fraud_status == 'accept':
#                     order.status = 'Accepted'
#                     order.is_ordered = True
#             elif transaction_status == 'settlement':
#                 # Settlement = Lunas (Contoh: Uang sudah masuk dari Indomaret/Bank)
#                 order.status = 'Accepted'
#                 order.is_ordered = True
#             elif transaction_status in ['cancel', 'deny', 'expire']:
#                 # Jika pembeli batal/kadaluarsa, ubah status jadi Cancelled
#                 order.status = 'Cancelled'
#                 order.is_ordered = False
                
#                 # (BONUS) KEMBALIKAN STOK SEPATU KARENA BATAL BELI
#                 order_products = OrderProduct.objects.filter(order=order)
#                 for item in order_products:
#                     product = item.product
#                     product.stock += item.quantity
#                     product.save()
                    
#             elif transaction_status == 'pending':
#                 order.status = 'Pending'

#             # 4. Simpan perubahan ke database
#             order.save()
            
#             # Beritahu Midtrans bahwa pesanannya sudah kita terima dengan sukses (Kode 200)
#             return HttpResponse('Sukses', status=200)

#         except Exception as e:
#             print(f"Error Webhook: {e}")
#             return HttpResponse('Server Error', status=500)
            
#     # Jika ada yang iseng mengakses URL ini lewat browser biasa (Metode GET)
#     return HttpResponse('Metode tidak diizinkan', status=405)


#Notifikasi Gmail
# from django.core.mail import send_mail
# from django.template.loader import render_to_string

# @csrf_exempt
# def midtrans_webhook(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         order_number = data.get('order_id')
#         transaction_status = data.get('transaction_status')

#         try:
#             order = Order.objects.get(order_number=order_number)
            
#             if transaction_status in ['capture', 'settlement']:
#                 if not order.is_ordered:
#                     # 1. Update Status Pesanan
#                     order.status = 'Accepted'
#                     order.is_ordered = True
#                     order.save()

#                     # 2. Kirim Email Notifikasi
#                     mail_subject = f'Pembayaran Berhasil - Pesanan #{order.order_number}'
#                     message = f"Halo {order.first_name},\n\nPembayaran Anda untuk pesanan #{order.order_number} telah kami terima. Kami akan segera memproses pengiriman sepatu Anda.\n\nTerima kasih telah berbelanja di DD Shoes Store!"
#                     to_email = order.email
                    
#                     send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])

#             return HttpResponse(status=200)
#         except Order.DoesNotExist:
#             return HttpResponse(status=404)
        

#Tracking Pesanan
def track_order(request):
    tracking_result = None
    error_message = None
    
    # Ambil data baik dari POST (form) maupun GET (link otomatis)
    resi = request.POST.get('no_resi') or request.GET.get('no_resi')
    kurir = request.POST.get('kurir') or request.GET.get('kurir')
    
    if resi and kurir:
        api_key = '9b016bd8ee7f7dadb64abc91f2fcead58f54abc72bf212f9f18de93f721522d1'
        url = f"https://api.binderbyte.com/v1/track?api_key={api_key}&courier={kurir}&awb={resi}"
        
        try:
            response = requests.get(url)
            data = response.json()
            if data['status'] == 200:
                tracking_result = data['data']
            else:
                error_message = data['message']
        except Exception as e:
            error_message = "Terjadi gangguan koneksi."

    return render(request, 'order/track.html', {
        'tracking_result': tracking_result, 
        'error_message': error_message,
        'resi': resi, # Kirim balik agar tampil di input box
        'kurir': kurir
    })
    

# =========================================================
# FUNGSI CETAK INVOICE PDF
# =========================================================    
def admin_order_pdf(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    order_products = OrderProduct.objects.filter(order=order)
    st = order.status
    if st == 'New':
        friendly_status = "Menunggu Pembayaran"
    elif st == 'Pending':
        friendly_status = "Pembayaran Berhasil"
    elif st == 'Accepted':
        if order.tracking_number: # Jika resi sudah diisi
            friendly_status = "Sedang Dikirim"
        else:
            friendly_status = "Sedang Diproses"
    elif st == 'Completed':
        friendly_status = "Pesanan Selesai"
    elif st == 'Cancelled':
        friendly_status = "Pesanan Dibatalkan"
    else:
        friendly_status = st # Jaga-jaga jika ada status lain
    template_path = 'order/invoice_pdf.html'
    context = {
        'order': order,
        'order_products': order_products,
        'friendly_status': friendly_status,
    }
    
    # Buat response PDF
    response = HttpResponse(content_type='application/pdf')
    # inline untuk buka di browser, attachment untuk langsung download
    response['Content-Disposition'] = f'filename="invoice_{order.order_number}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # Convert HTML ke PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat mencetak PDF')
    return response


#Fungsi Order Selesai ada voucher juga
def order_complete(request, order_number):
    try:
        order = Order.objects.filter(order_number=order_number, user=request.user).first()
        
        if order is None:
            return redirect('home')

        if order.status == 'Accepted':
            order.is_ordered = True
            order.status = 'Completed'
            order.save() 



        return render(request, 'order/confirmation.html', {'order': order})

    except Exception as e:
        print(f"Error pada order_complete: {e}")
        return redirect('home')

    

#FUNGSI RETUR PRODUK
def submit_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # --- LOGIKA BARU: Cek apakah status sudah 'Accepted' dan Resi sudah ada ---
    if order.status != 'Accepted' or not order.tracking_number:
        messages.error(request, 'Retur hanya bisa diajukan saat pesanan sedang dalam proses pengiriman.')
        return redirect('my_orders')

    # Cek apakah sudah pernah mengajukan retur sebelumnya (untuk menghindari double submit)
    if hasattr(order, 'return_request'):
        messages.warning(request, 'Anda sudah mengajukan retur untuk pesanan ini.')
        return redirect('my_orders')

    if request.method == 'POST':
        form = ReturnRequestForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.order = order
            # Opsional: Jika ingin status pesanan langsung berubah saat retur diajukan
            # order.status = 'Refund' 
            # order.save()
            
            data.save()
            messages.success(request, 'Permintaan retur berhasil dikirim. Mohon tunggu konfirmasi admin.')
            return redirect('my_orders')
    else:
        form = ReturnRequestForm()

    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'order/submit_return.html', context)


#Voucher
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        
        # --- PERBAIKAN: Hapus diskon lama sebelum cek yang baru ---
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        if 'discount_amount' in request.session:
            del request.session['discount_amount']
            
        try:
            # Cek kupon baru
            coupon = Coupon.objects.get(code=code, user=request.user, is_used=False)
            
            request.session['coupon_id'] = coupon.id
            request.session['discount_amount'] = coupon.discount_value
            messages.success(request, f"Kupon {code} berhasil digunakan!")
            
        except Coupon.DoesNotExist:
            messages.error(request, "Kupon tidak valid, sudah dipakai, atau salah ketik.")
            # Karena sudah dihapus di atas, maka jika salah, diskon otomatis jadi 0
            
    return redirect('cart')

def reset_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    return redirect('cart')