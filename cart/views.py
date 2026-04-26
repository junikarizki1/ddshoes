from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# IMPORT PELINDUNG LOGIN
from django.contrib.auth.decorators import login_required

# 1. Tambah Item (Dilindungi wajib login)
@login_required(login_url='login')
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    # Kita tidak lagi pakai cart session, langsung hubungkan ke user
    try:
        cart_item = CartItem.objects.get(product=product, user=current_user)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            user=current_user, # Menghubungkan barang dengan user yang login
        )
        cart_item.save()
    
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
    # Inisialisasi awal agar tidak error jika try gagal
    discount = 0
    grand_total = 0
    
    try:
        # 1. Ambil item keranjang milik user
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        # 2. Hitung total harga barang
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # 3. LOGIKA DISKON KUPON
        # Ambil nilai diskon dari session (hasil dari fungsi apply_coupon)
        discount = request.session.get('discount_amount', 0)
        
        # 4. HITUNG GRAND TOTAL
        # Harga barang dikurangi diskon (jika ada)
        grand_total = total - discount
        
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'discount': discount,       # Tambahkan ini agar bisa dipanggil di HTML
        'grand_total': grand_total, # Sekarang variabel ini sudah aman didefinisikan
    }
    
    return render(request, 'cart/cart.html', context)