from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand
from django.db.models import Q 

def home(request):
    return render(request, 'home.html')

def product(request, category_slug=None):
    categories = None
    products = None

    # --- A. Logika Dasar (Filter Kategori atau Tampilkan Semua) ---
    if category_slug != None:
        # Jika URL memiliki slug kategori (misal: /store/category/sneakers/)
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        # Jika URL polos (/product/ atau /store/), tampilkan semua produk
        products = Product.objects.all().filter(is_available=True).order_by('id')

    # --- B. Logika Search (Pencarian Nama) ---
    # Mengambil nilai dari ?q=... di URL
    query = request.GET.get('q')
    if query:
        # Filter produk berdasarkan nama ATAU deskripsi
        products = products.filter(Q(product_name__icontains=query) | Q(description__icontains=query))

    # --- C. Logika Filter Brand (BARU) ---
    # Mengambil nilai dari ?brand=... di URL
    brand_id = request.GET.get('brand')
    if brand_id:
        # Filter produk berdasarkan ID brand
        products = products.filter(brand__id=brand_id)
    
    # --- D. Data Pendukung ---
    product_count = products.count()      # Hitung jumlah produk hasil filter
    all_categories = Category.objects.all() # Ambil semua kategori untuk Sidebar
    all_brands = Brand.objects.all()        # Ambil semua brand untuk Sidebar

    context = {
        'products': products,
        'product_count': product_count,
        'categories': all_categories,
        'brands': all_brands,        # Data brand dikirim ke template
        'query': query,              # Query search dikirim balik agar search bar tidak hilang teksnya
    }
        # --- TAMBAHAN: Hitung Total Semua Produk untuk opsi 'All' ---
    all_products_count = Product.objects.filter(is_available=True).count()

    context = {
        'products': products,
        'product_count': product_count,
        'categories': all_categories,
        'brands': all_brands,
        'query': query,
        # Kirim ke template
        'all_products_count': all_products_count, 
    }
    
    
    # Menggunakan template 'store.html' (Halaman Katalog)
    return render(request, 'store/product.html', context)

# ==========================================
# 3. VIEW DETAIL PRODUK (PERBAIKAN UTAMA)
# ==========================================
# Perhatikan parameter di dalam kurung: (request, category_slug, product_slug)
# Ini WAJIB ada agar sesuai dengan URL path di urls.py
def product_detail(request, category_slug, product_slug):
    try:
        # Mencari 1 produk spesifik yang punya kategori & slug sesuai URL
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e 

    context = {
        'single_product': single_product,
    }
    # Pastikan template product_detail.html sudah ada di folder store/templates/store/
    return render(request, 'store/product_detail.html', context)