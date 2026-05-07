from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand, UserInterest
from django.db.models import Q, Case, When, Value, IntegerField, Sum 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import random
from decimal import Decimal
from django.db.models import Count
from order.models import OrderProduct
from django.db.models.functions import Coalesce

def home(request):
    # Ambil semua produk yang tersedia dan memiliki stok
    all_available = Product.objects.filter(is_available=True, stock__gt=0)
    recommended_products = []
    
    if request.user.is_authenticated:
        user = request.user
        # Ambil data minat user dari database
        user_interests = UserInterest.objects.filter(user=user)
        
        # Cek apakah user sudah mulai melakukan interaksi (klik produk)
        has_interest = user_interests.exists()
        
        if not has_interest:
            # --- SKENARIO A: USER BARU (Cold Start) ---
            # Prioritaskan produk yang ukurannya pas dengan shoe_size user
            personalized_queryset = all_available.annotate(
                priority=Case(
                    When(size=user.shoe_size, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('priority', '-created_date')[:4]
        
        else:
            # --- SKENARIO B: USER AKTIF (Content-Based) ---
            # Ambil Brand dan Kategori yang paling sering diklik
            top_brand = user_interests.filter(brand__isnull=False).order_by('-score').first()
            top_cat = user_interests.filter(category__isnull=False).order_by('-score').first()
            
            personalized_queryset = all_available.annotate(
                priority=Case(
                    # P1: Ukuran Pas + Brand Favorit
                    When(size=user.shoe_size, brand=top_brand.brand if top_brand else None, then=Value(1)),
                    # P2: Ukuran Pas + Kategori Favorit
                    When(size=user.shoe_size, category=top_cat.category if top_cat else None, then=Value(2)),
                    # P3: Ukuran Pas saja
                    When(size=user.shoe_size, then=Value(3)),
                    # P4: Brand Favorit saja
                    When(brand=top_brand.brand if top_brand else None, then=Value(4)),
                    # P5: Kategori Favorit saja
                    When(category=top_cat.category if top_cat else None, then=Value(5)),
                    default=Value(6),
                    output_field=IntegerField(),
                )
            ).order_by('priority', '-created_date')[:4]

        recommended_products = list(personalized_queryset)
    
    else:
        # --- SKENARIO C: GUEST / ANONIM ---
        # Tampilkan 4 produk terbaru secara umum
        recommended_products = list(all_available.order_by('-created_date')[:4])

    # --- LOGIKA DISCOVERY (2 Produk Tambahan) ---
    # Mengambil 2 produk secara acak untuk melengkapi total 6 produk di Home
    # Mengecualikan produk yang sudah masuk dalam daftar personalisasi
    excluded_ids = [p.id for p in recommended_products]
    discovery_products = all_available.exclude(id__in=excluded_ids).order_by('?')[:2]
    
    # Gabungkan 4 produk personalisasi + 2 produk discovery
    final_recommendations = recommended_products + list(discovery_products)
    
    
    #TOP KATEGORI
    top_categories = Category.objects.annotate(
        total_sold=Coalesce(
            Sum('product__orderproduct__quantity', filter=Q(product__orderproduct__ordered=True)),
            Value(0)
        )
    ).order_by('-total_sold')[:3]
    
    #TOP BRAND
    top_brands = Brand.objects.annotate(
        brand_sales=Coalesce(
            Sum('product__orderproduct__quantity', filter=Q(product__orderproduct__ordered=True)),
            Value(0)
        )
    ).order_by('-brand_sales')[:5]

    context = {
        'recommended_products': final_recommendations,
        'top_categories': top_categories,
        'top_brands': top_brands,
    }
    return render(request, 'home.html', context)
    

    

def product(request, category_slug=None, brand_slug=None):
    # --- A. Logika Dasar (Filter Kategori atau Tampilkan Semua) ---
    if category_slug is not None:
        # Jika URL memiliki slug kategori (misal: /store/category/sneakers/)
        current_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=current_category, is_available=True)
    elif brand_slug != None:
        # Filter berdasarkan brand
        brands = get_object_or_404(Brand, slug=brand_slug)
        products = Product.objects.filter(brand=brands, is_available=True)
    else:
        # Jika URL polos (/product/ atau /store/), tampilkan semua produk
        products = Product.objects.filter(is_available=True).order_by('id')


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
        'all_products_count': all_products_count,
        'category_slug': category_slug, # PENTING: Untuk menandai radio button kategori mana yang aktif
        'brand_slug': brand_slug,
    }
    
    return render(request, 'store/product.html', context)

#Fungsi Search Produk
def search(request):
    # 1. Inisialisasi variabel dengan nilai kosong/default
    products = None
    product_count = 0
    keyword = ""

    # 2. Cek apakah ada parameter keyword di URL
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword', '') # Ambil keyword, default string kosong
        
        if keyword:
            # Cari produk berdasarkan nama atau deskripsi
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
        else:
            # Jika keyword dikirim tapi kosong (search kosong)
            products = Product.objects.all().order_by('-created_date')
            product_count = products.count()
    else:
        # Jika akses langsung ke /search/ tanpa parameter keyword
        products = Product.objects.all().order_by('-created_date')
        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'keyword': keyword,
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
    
    # LOGIKA TRACKING PERSONALISASI
    if request.user.is_authenticated:
        # Panggil fungsi untuk update poin (bisa dibuat helper atau tulis langsung)
        update_user_interest(request.user, single_product, action_weight=1) # 1 poin untuk klik/view

    context = {
        'single_product': single_product,
    }
    # Pastikan template product_detail.html sudah ada di folder store/templates/store/
    return render(request, 'store/product_detail.html', context)

def update_user_interest(user, product, action_weight):
    # 1. Update/Buat poin untuk Brand
    brand_interest, _ = UserInterest.objects.get_or_create(user=user, brand=product.brand)
    brand_interest.score += action_weight
    brand_interest.save()

    # 2. Update/Buat poin untuk Kategori
    cat_interest, _ = UserInterest.objects.get_or_create(user=user, category=product.category)
    cat_interest.score += action_weight
    cat_interest.save()