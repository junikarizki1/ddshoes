from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# IMPORT PELINDUNG LOGIN
from django.contrib.auth.decorators import login_required

# 1. Tambah Item (Dilindungi wajib login)
@login_required(login_url='login')
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, user=current_user)
        
        # VALIDASI: Cek apakah jumlah yang ingin ditambah melebihi stok yang ada
        if cart_item.quantity + 1 > product.stock:
            messages.error(request, f"Maaf, stok {product.product_name} hanya tersisa {product.stock}.")
            return redirect('cart')
        
        cart_item.quantity += 1
        cart_item.save()
        
    except CartItem.DoesNotExist:
        # VALIDASI: Cek stok bahkan saat pertama kali membuat item (jika stok 0)
        if product.stock > 0:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            cart_item.save()
        else:
            messages.error(request, f"Maaf, stok {product.product_name} sedang kosong.")
            return redirect('cart')
    
    return redirect('cart')

# 2. Kurangi Item (Dilindungi wajib login)
@login_required(login_url='login')
def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        # Cari barang di keranjang berdasarkan user yang sedang login
        cart_item = CartItem.objects.get(product=product, user=request.user)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

# 3. Hapus Item Sepenuhnya (Dilindungi wajib login)
@login_required(login_url='login')
def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, user=request.user)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

# 4. Halaman Cart (Dilindungi wajib login)
@login_required(login_url='login')
def cart(request, total=0, quantity=0, cart_items=None):
    # 1. Ambil data dari session
    coupon_id = request.session.get('coupon_id')
    
    # 2. VALIDASI OTOMATIS (Tanpa menghapus paksa)
    if coupon_id:
        try:
            from .models import Coupon
            # Cek apakah kupon ID di session ini memang masih ada di database dan belum dipakai
            coupon = Coupon.objects.filter(id=coupon_id, is_used=False).first()
            
            if not coupon:
                # Jika kupon sudah dihapus dari admin atau sudah dipakai, baru kita bersihkan session
                request.session.pop('coupon_id', None)
                request.session.pop('discount_amount', None)
                request.session.modified = True
        except:
            pass

    # 3. Ambil nilai diskon terbaru dari session setelah divalidasi
    discount = request.session.get('discount_amount', 0)
    
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # 4. Hitung Grand Total
        grand_total = total - discount
        
    except ObjectDoesNotExist:
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'discount': discount,
        'grand_total': grand_total,
    }
    return render(request, 'cart/cart.html', context)