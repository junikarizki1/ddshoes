from .models import Brand, Product

def menu_links_brand(request):
    # Mengambil semua data brand untuk ditampilkan di sidebar
    links_brand = Brand.objects.all()
    # Menghitung semua produk untuk opsi "Semua Brand"
    all_products_count = Product.objects.filter(is_available=True).count()
    
    return {
        'links_brand': links_brand,
        'all_products_count': all_products_count,
    }