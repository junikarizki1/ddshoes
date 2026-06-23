import requests
import datetime
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import CartItem 
from .models import Order, OrderProduct, Coupon
from account.models import Address
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
from store.models import ReviewRating



# =========================================================
# API KEY KOMERCE ANDA
# =========================================================
KOMERCE_API_KEY = settings.KOMERCE_API_KEY 

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += float(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
        discount = float(request.session.get('discount_amount', 0))
        total = total - discount
    except ObjectDoesNotExist:
        pass
        
    if quantity <= 0:
        return redirect('product')
    
    # Cache provinsi di session untuk menghemat API call
    if 'rajaongkir_provinces' not in request.session:
        provinces = []
        try:
            url = "https://rajaongkir.komerce.id/api/v1/destination/province"
            headers = {'key': KOMERCE_API_KEY}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                provinces = data.get('data', [])
                request.session['rajaongkir_provinces'] = provinces
        except Exception as e:
            print(f"ERROR SYSTEM: {e}")
    else:
        provinces = request.session['rajaongkir_provinces']
    
    # Pass semua alamat user ke template
    user = request.user
    user_addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    default_address = user_addresses.filter(is_default=True).first()
    
    # Ambil voucher user yang belum dipakai
    available_coupons = Coupon.objects.filter(user=user, is_used=False).order_by('-created_at')
    active_coupon_id = request.session.get('coupon_id')
    
    context = {
        'total': total,
        'discount': discount,
        'grand_total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'provinces': provinces,
        'user_addresses': user_addresses,
        'default_address': default_address,
        'has_saved_address': user_addresses.exists(),
        'available_coupons': available_coupons,
        'active_coupon_id': active_coupon_id,
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
            print(f"Komerce API Status: {response.status_code}")
            print(f"Komerce API Response: {response.text[:200]}")
            if response.status_code == 200:
                results = response.json().get('data', [])
                print(f"Parsed results count: {len(results)}")
            else:
                print(f"Komerce API Error: {response.text}")
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
    
    # 1. Validasi Keranjang
    if cart_items.count() <= 0:
        return redirect('home')

    # 2. Hitung Total Harga Produk (Gross)
    for cart_item in cart_items:
        total += float(cart_item.product.price) * cart_item.quantity
        quantity += cart_item.quantity

    if request.method == 'POST':
        # --- AMBIL DATA DARI REQUEST & SESSION ---
        try:
            shipping_cost = float(request.POST.get('shipping_cost', 0))
        except (ValueError, TypeError):
            shipping_cost = 0.0
            
        discount = float(request.session.get('discount_amount', 0))
        coupon_id = request.session.get('coupon_id')
        
        # --- KALKULASI FINANSIAL ---
        # Net Revenue / Omzet Bersih (Harga Produk - Diskon)
        order_total_net = float(total) - discount
        # Tagihan Akhir ke User
        grand_total = order_total_net + shipping_cost

        # 3. Simpan Objek Order (Data Utama)
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
        data.postal_code = request.POST.get('postal_code')
        data.order_note = request.POST.get('order_note')
        data.shipping_service = request.POST.get('shipping_service')
        
        # Menyimpan rincian biaya secara mendalam (Audit Trail)
        data.order_total = order_total_net  # Ini yang dipanggil sebagai Omzet
        data.discount = discount           # Field baru untuk menyimpan riwayat diskon
        data.shipping_cost = shipping_cost
        data.grand_total = grand_total
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        # 4. Generate Order Number
        current_date = datetime.date.today().strftime("%Y%m%d") 
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        # 5. Penguncian Voucher (Is Used)
        if coupon_id:
            try:
                voucher = Coupon.objects.get(id=coupon_id, user=current_user)
                voucher.is_used = True
                voucher.save()
            except Coupon.DoesNotExist:
                pass

        # 5b. Handle Alamat: Gunakan alamat tersimpan atau simpan baru secara otomatis
        selected_address_id = request.POST.get('selected_address_id')
        if selected_address_id:
            # User memilih alamat tersimpan
            try:
                selected_addr = Address.objects.get(id=selected_address_id, user=current_user)
            except Address.DoesNotExist:
                selected_addr = None
        else:
            selected_addr = None

        if not selected_addr:
            # Otomatis simpan alamat baru (dan tidak memilih alamat tersimpan)
            if Address.objects.filter(user=current_user).count() < 3:
                Address.objects.create(
                    user=current_user,
                    label=request.POST.get('address_label', 'Alamat Baru'),
                    province_id=request.POST.get('province_id', ''),
                    province_name=request.POST.get('province', ''),
                    city_id=request.POST.get('city_id', ''),
                    city_name=request.POST.get('city', ''),
                    district_id=request.POST.get('district_id', ''),
                    district_name=request.POST.get('district', ''),
                    subdistrict_id=request.POST.get('subdistrict_id', ''),
                    subdistrict_name=request.POST.get('subdistrict', ''),
                    postal_code=request.POST.get('postal_code', ''),
                    address=request.POST.get('address', ''),
                    shipping_service=request.POST.get('shipping_service', ''),
                    shipping_cost=shipping_cost,
                )

        # 6. Pindahkan Item ke OrderProduct & Update Stok
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = data.id
            orderproduct.user_id = current_user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = float(item.product.price)
            orderproduct.ordered = True
            orderproduct.save()

            # Pengurangan Stok Produk
            product = item.product
            product.stock -= int(item.quantity)
            product.save()

        # 7. Pembersihan Akhir (Clean Up)
        cart_items.delete() # Hapus item keranjang
        
        # Hapus session agar tidak mengganggu transaksi berikutnya
        session_keys = ['discount_amount', 'coupon_id', 'coupon_code']
        for key in session_keys:
            if key in request.session:
                del request.session[key]

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

    # Gunakan snap_token yang sudah ada jika masih tersimpan.
    # Midtrans MENOLAK pembuatan transaksi baru dengan order_id yang sama
    # selama transaksi lama masih pending — ini penyebab user tidak bisa
    # melanjutkan pembayaran setelah menunda.
    snap_token = order.snap_token if order.snap_token else None

    if not snap_token:
        # Belum ada token sama sekali → buat baru
        item_list = []

        for item in order_products:
            item_list.append({
                "id": f"PROD-{item.product.id}",
                "price": int(float(item.product_price)),
                "quantity": item.quantity,
                "name": item.product.product_name[:30]
            })

        item_list.append({
            "id": "SHIPPING",
            "price": int(float(order.shipping_cost)),
            "quantity": 1,
            "name": "Ongkos Kirim"
        })

        total_normal = sum(float(item.product_price) * item.quantity for item in order_products) + float(order.shipping_cost)
        discount_amount = total_normal - float(order.grand_total)

        if discount_amount > 1:
            item_list.append({
                "id": "DISCOUNT-LOYALTY",
                "price": -int(discount_amount),
                "quantity": 1,
                "name": "Potongan Voucher"
            })

        param = {
            "transaction_details": {
                "order_id": order.order_number,
                "gross_amount": int(float(order.grand_total))
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
            has_reviewed = False
            if order.status == 'Completed':
                has_reviewed = ReviewRating.objects.filter(order=order).exists()
            context = {'order': order, 'has_reviewed': has_reviewed}
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

    context = {
            'order': order,
        }
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

        if order.status != 'Completed':
            order.status = 'Completed'
            order.save()

        has_reviewed = ReviewRating.objects.filter(order=order).exists()

        context = {
            'order': order,
            'has_reviewed': has_reviewed,
        }
        return render(request, 'order/confirmation.html', context)
    except Exception as e:
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
        coupon_id = request.POST.get('coupon_id')
        code = request.POST.get('coupon_code')
        
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        if 'discount_amount' in request.session:
            del request.session['discount_amount']
            
        try:
            if coupon_id:
                coupon = Coupon.objects.get(id=coupon_id, user=request.user, is_used=False)
            else:
                coupon = Coupon.objects.get(code=code, user=request.user, is_used=False)
            
            request.session['coupon_id'] = coupon.id
            request.session['discount_amount'] = coupon.discount_value
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'discount': coupon.discount_value})
            
            messages.success(request, f"Kupon {coupon.code} berhasil digunakan!")
            
        except Coupon.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Voucher tidak valid'})
            messages.error(request, "Voucher tidak valid, sudah dipakai, atau salah ketik.")
            
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def reset_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
        
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

