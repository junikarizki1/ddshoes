from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand
from django.db.models import Q 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def home(request):
    # Mengambil semua produk yang tersedia
    products = Product.objects.all().filter(is_available=True) 
    
    context = {
        'products': products, # <-- Data ini yang akan kita looping
    }
    return render(request, 'home.html', context)

def product(request, category_slug=None):
    # --- A. Logika Dasar (Filter Kategori atau Tampilkan Semua) ---
    if category_slug is not None:
        # Jika URL memiliki slug kategori (misal: /store/category/sneakers/)
        current_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=current_category, is_available=True)
    else:
        # Jika URL polos (/product/ atau /store/), tampilkan semua produk
        products = Product.objects.filter(is_available=True).order_by('id')

    # --- B. Logika Search (Pencarian Nama) ---
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(product_name__icontains=query) | Q(description__icontains=query))

    # --- C. Logika Filter Brand ---
    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(brand__id=brand_id)
        
    
    # --- LOGIKA PAGINATION ---
    # 1. Tentukan berapa produk per halaman (misal: 6 atau 12)
    paginator = Paginator(products, 6) 
    # 2. Ambil nomor halaman dari URL (misal: ?page=2)
    page = request.GET.get('page')
    # 3. Ambil produk untuk halaman tersebut
    paged_products = paginator.get_page(page)
    
    # --- D. Data Pendukung & Context ---
    product_count = products.count()
    all_categories = Category.objects.all()
    all_brands = Brand.objects.all()
    all_products_count = Product.objects.filter(is_available=True).count()

    # Gabungkan semua data ke dalam satu context agar tidak tertimpa
    context = {
        'products': paged_products,
        'product_count': product_count,
        'categories': all_categories,
        'brands': all_brands,
        'query': query,
        'all_products_count': all_products_count,
        'category_slug': category_slug, # PENTING: Untuk menandai radio button kategori mana yang aktif
    }
    
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