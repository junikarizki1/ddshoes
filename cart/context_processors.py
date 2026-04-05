from .models import CartItem

def cart_count(request):
    count = 0
    # Hanya hitung jika user sudah login
    if request.user.is_authenticated:
        try:
            # Ambil semua barang milik user ini
            cart_items = CartItem.objects.filter(user=request.user)
            # Jumlahkan qty (quantity) dari setiap barang
            for cart_item in cart_items:
                count += cart_item.quantity
        except CartItem.DoesNotExist:
            count = 0
            
    # Kembalikan sebagai kamus/dictionary agar bisa dibaca oleh HTML
    return dict(cart_count=count)