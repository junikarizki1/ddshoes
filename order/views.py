from django.shortcuts import render

def checkout(request):
    # Logika untuk form alamat, pembayaran, dan total harga akan ditaruh di sini nantinya.
    # Untuk sementara, kita langsung tampilkan halaman konfirmasinya.
    
    # Pastikan nama folder template Anda sesuai, misal: order/confirmation.html
    return render(request, 'order/checkout.html')

def confirmation(request):
    
    return render(request, 'order/confirmation.html')