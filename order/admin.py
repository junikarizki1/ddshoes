from django.contrib import admin
from django.db.models import Sum, Q, Count, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Order, OrderProduct, Coupon, Account
from store.models import Product, Brand, Category, ReviewRating, UserInterest
from account.models import Account as UserAccount
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.urls import reverse
from .models import ReturnRequest

# --- 1. FILTER CUSTOM UNTUK TABEL ORDER ---
class TrackingFilter(SimpleListFilter):
    title = 'Status Resi'
    parameter_name = 'resi'

    def lookups(self, request, model_admin):
        return (
            ('empty', 'Belum Isi Resi'),
            ('filled', 'Sudah Isi Resi'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'empty':
            return queryset.filter(Q(tracking_number__isnull=True) | Q(tracking_number=''))
        if self.value() == 'filled':
            return queryset.exclude(Q(tracking_number__isnull=True) | Q(tracking_number=''))

# --- 2. FUNGSI HITUNG STATISTIK DASHBOARD ---
from django.db.models.functions import TruncDate
from collections import defaultdict

def get_dashboard_data(period=None, start_custom=None, end_custom=None):
    orders = Order.objects.all()
    returns = ReturnRequest.objects.all()
    now = timezone.now()

    # Logika Filter Tanggal (Bebas / Shortcut) untuk Order dan Retur
    if start_custom and end_custom:
        orders = orders.filter(created_at__date__range=[start_custom, end_custom])
        returns = returns.filter(created_at__date__range=[start_custom, end_custom])
    elif period == 'today':
        orders = orders.filter(created_at__date=now.date())
        returns = returns.filter(created_at__date=now.date())
    elif period == 'week':
        orders = orders.filter(created_at__gte=now - timedelta(days=7))
        returns = returns.filter(created_at__gte=now - timedelta(days=7))
    elif period == 'month':
        orders = orders.filter(created_at__year=now.year, created_at__month=now.month)
        returns = returns.filter(created_at__year=now.year, created_at__month=now.month)
    elif period == 'year':
        orders = orders.filter(created_at__year=now.year)
        returns = returns.filter(created_at__year=now.year)

    # Filter Model Lain (UserAccount, Coupon, ReviewRating, UserInterest) dengan rentang yang sama
    users_qs = UserAccount.objects.all()
    coupons_filtered = Coupon.objects.all()
    reviews_filtered = ReviewRating.objects.all()
    interests_filtered = UserInterest.objects.all()

    if start_custom and end_custom:
        users_qs = users_qs.filter(date_joined__date__range=[start_custom, end_custom])
        coupons_filtered = coupons_filtered.filter(created_at__date__range=[start_custom, end_custom])
        reviews_filtered = reviews_filtered.filter(created_at__date__range=[start_custom, end_custom])
        interests_filtered = interests_filtered.filter(last_action__date__range=[start_custom, end_custom])
    elif period == 'today':
        users_qs = users_qs.filter(date_joined__date=now.date())
        coupons_filtered = coupons_filtered.filter(created_at__date=now.date())
        reviews_filtered = reviews_filtered.filter(created_at__date=now.date())
        interests_filtered = interests_filtered.filter(last_action__date=now.date())
    elif period == 'week':
        users_qs = users_qs.filter(date_joined__gte=now - timedelta(days=7))
        coupons_filtered = coupons_filtered.filter(created_at__gte=now - timedelta(days=7))
        reviews_filtered = reviews_filtered.filter(created_at__gte=now - timedelta(days=7))
        interests_filtered = interests_filtered.filter(last_action__gte=now - timedelta(days=7))
    elif period == 'month':
        users_qs = users_qs.filter(date_joined__year=now.year, date_joined__month=now.month)
        coupons_filtered = coupons_filtered.filter(created_at__year=now.year, created_at__month=now.month)
        reviews_filtered = reviews_filtered.filter(created_at__year=now.year, created_at__month=now.month)
        interests_filtered = interests_filtered.filter(last_action__year=now.year, last_action__month=now.month)
    elif period == 'year':
        users_qs = users_qs.filter(date_joined__year=now.year)
        coupons_filtered = coupons_filtered.filter(created_at__year=now.year)
        reviews_filtered = reviews_filtered.filter(created_at__year=now.year)
        interests_filtered = interests_filtered.filter(last_action__year=now.year)
    
    # Hitung Statistik
    revenue = orders.filter(status='Completed').aggregate(Sum('order_total'))['order_total__sum'] or 0
    unpaid_orders = orders.filter(status='New').count()
    
    # Siap Pack = Accepted & Resi Kosong
    to_ship = orders.filter(
        Q(status='Accepted') & (Q(tracking_number__isnull=True) | Q(tracking_number=''))
    ).count()

    # Sedang Dikirim = Accepted & Resi Ada
    shipping = orders.filter(
        status='Accepted'
    ).exclude(Q(tracking_number__isnull=True) | Q(tracking_number='')).count()
    
    completed = orders.filter(status='Completed').count()
    cancelled = orders.filter(status='Cancelled').count()
    total_orders = orders.count()
    
    # Inventori (Tetap dihitung total, tidak kena filter tanggal)
    out_of_stock = Product.objects.filter(stock=0).count()
    low_stock = Product.objects.filter(stock=1).count()
    
    # --- HITUNG STATISTIK RETUR ---
    retur_pending = returns.filter(status='Pending').count()
    retur_proses  = returns.filter(status='Approved').count()
    retur_selesai = max(returns.filter(status='Refunded').count(), orders.filter(status='Returned').count())
    retur_ditolak = returns.filter(status='Rejected').count()
    
    # --- DATA GRAFIK PENJUALAN (REAL DATA) ---
    chart_labels = []
    chart_order_data = []
    chart_revenue_data = []
    
    if period == 'today':
        # Per jam untuk hari ini
        for hour in range(24):
            label = f"{hour:02d}:00"
            hour_orders = orders.filter(created_at__hour=hour).count()
            hour_revenue = orders.filter(created_at__hour=hour, status='Completed').aggregate(Sum('order_total'))['order_total__sum'] or 0
            chart_labels.append(label)
            chart_order_data.append(hour_orders)
            chart_revenue_data.append(hour_revenue)
    elif period == 'week' or (start_custom and end_custom and (datetime.strptime(end_custom, '%Y-%m-%d') - datetime.strptime(start_custom, '%Y-%m-%d')).days <= 14):
        # Per hari untuk 7-14 hari terakhir
        daily_data = defaultdict(lambda: {'count': 0, 'revenue': 0})
        for order in orders:
            day_key = order.created_at.date()
            daily_data[day_key]['count'] += 1
            if order.status == 'Completed':
                daily_data[day_key]['revenue'] += order.order_total
        
        if start_custom and end_custom:
            d = datetime.strptime(start_custom, '%Y-%m-%d').date()
            end = datetime.strptime(end_custom, '%Y-%m-%d').date()
        else:
            d = (now - timedelta(days=7)).date()
            end = now.date()
        
        while d <= end:
            chart_labels.append(d.strftime('%d/%m'))
            chart_order_data.append(daily_data[d]['count'])
            chart_revenue_data.append(daily_data[d]['revenue'])
            d += timedelta(days=1)
    elif period == 'month':
        # Per hari untuk bulan ini
        daily_data = defaultdict(lambda: {'count': 0, 'revenue': 0})
        for order in orders:
            day_key = order.created_at.date()
            daily_data[day_key]['count'] += 1
            if order.status == 'Completed':
                daily_data[day_key]['revenue'] += order.order_total
        
        import calendar
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        for day in range(1, days_in_month + 1):
            d = datetime(now.year, now.month, day).date()
            chart_labels.append(str(day))
            chart_order_data.append(daily_data[d]['count'])
            chart_revenue_data.append(daily_data[d]['revenue'])
    elif period == 'year':
        # Per bulan untuk tahun ini
        monthly_data = defaultdict(lambda: {'count': 0, 'revenue': 0})
        for order in orders:
            month_key = order.created_at.month
            monthly_data[month_key]['count'] += 1
            if order.status == 'Completed':
                monthly_data[month_key]['revenue'] += order.order_total
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
        for m in range(1, 13):
            chart_labels.append(month_names[m-1])
            chart_order_data.append(monthly_data[m]['count'])
            chart_revenue_data.append(monthly_data[m]['revenue'])
    else:
        # Default: 7 hari terakhir
        daily_data = defaultdict(lambda: {'count': 0, 'revenue': 0})
        for order in orders:
            day_key = order.created_at.date()
            daily_data[day_key]['count'] += 1
            if order.status == 'Completed':
                daily_data[day_key]['revenue'] += order.order_total
        
        d = (now - timedelta(days=7)).date()
        end = now.date()
        while d <= end:
            chart_labels.append(d.strftime('%d/%m'))
            chart_order_data.append(daily_data[d]['count'])
            chart_revenue_data.append(daily_data[d]['revenue'])
            d += timedelta(days=1)
    
    # --- DATA 5 PRODUK TERLARIS (TERFILTER) ---
    top_products = OrderProduct.objects.filter(order__in=orders).values('product__product_name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    top_products_labels = []
    top_products_data = []
    for p in top_products:
        name = p['product__product_name']
        if len(name) > 30:
            name = name[:27] + '...'
        top_products_labels.append(name)
        top_products_data.append(p['total_sold'] or 0)
    
    if not top_products_labels:
        top_products_labels = ['Belum ada data']
        top_products_data = [0]
    
    # --- DATA BRAND TERLARIS (TERFILTER) ---
    top_brands = OrderProduct.objects.filter(order__in=orders).values(
        'product__brand__brand_name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    brand_labels = []
    brand_data = []
    for b in top_brands:
        name = b['product__brand__brand_name'] or 'Tanpa Brand'
        brand_labels.append(name)
        brand_data.append(b['total_sold'] or 0)
    
    if not brand_labels:
        brand_labels = ['Belum ada data']
        brand_data = [0]
    
    # --- DATA CATEGORY TERLARIS (TERFILTER) ---
    top_categories = OrderProduct.objects.filter(order__in=orders).values(
        'product__category__category_name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    category_labels = []
    category_data = []
    for c in top_categories:
        name = c['product__category__category_name'] or 'Tanpa Kategori'
        category_labels.append(name)
        category_data.append(c['total_sold'] or 0)
    
    if not category_labels:
        category_labels = ['Belum ada data']
        category_data = [0]
    
    # --- DATA REGISTRASI USER (TERFILTER) ---
    user_chart_labels = []
    user_chart_data = []
    
    if period == 'today':
        for hour in range(24):
            label = f"{hour:02d}:00"
            count = users_qs.filter(date_joined__hour=hour).count()
            user_chart_labels.append(label)
            user_chart_data.append(count)
    elif period == 'week' or (start_custom and end_custom and (datetime.strptime(end_custom, '%Y-%m-%d') - datetime.strptime(start_custom, '%Y-%m-%d')).days <= 14):
        daily_users = defaultdict(int)
        for user in users_qs:
            day_key = user.date_joined.date()
            daily_users[day_key] += 1
        
        if start_custom and end_custom:
            d = datetime.strptime(start_custom, '%Y-%m-%d').date()
            end = datetime.strptime(end_custom, '%Y-%m-%d').date()
        else:
            d = (now - timedelta(days=7)).date()
            end = now.date()
        
        while d <= end:
            user_chart_labels.append(d.strftime('%d/%m'))
            user_chart_data.append(daily_users[d])
            d += timedelta(days=1)
    elif period == 'month':
        daily_users = defaultdict(int)
        for user in users_qs:
            day_key = user.date_joined.date()
            daily_users[day_key] += 1
        
        import calendar
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        for day in range(1, days_in_month + 1):
            d = datetime(now.year, now.month, day).date()
            user_chart_labels.append(str(day))
            user_chart_data.append(daily_users[d])
    elif period == 'year':
        monthly_users = defaultdict(int)
        for user in users_qs:
            month_key = user.date_joined.month
            monthly_users[month_key] += 1
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
        for m in range(1, 13):
            user_chart_labels.append(month_names[m-1])
            user_chart_data.append(monthly_users[m])
    else:
        # Default: 7 hari terakhir
        daily_users = defaultdict(int)
        fallback_users = UserAccount.objects.filter(date_joined__gte=now - timedelta(days=7))
        for user in fallback_users:
            day_key = user.date_joined.date()
            daily_users[day_key] += 1
        
        d = (now - timedelta(days=7)).date()
        end = now.date()
        while d <= end:
            user_chart_labels.append(d.strftime('%d/%m'))
            user_chart_data.append(daily_users[d])
            d += timedelta(days=1)
    
    # --- DATA PENGGUNAAN VOUCHER (TERFILTER) ---
    voucher_used = coupons_filtered.filter(is_used=True).count()
    voucher_unused = coupons_filtered.filter(is_used=False).count()
    voucher_labels = ['Sudah Dipakai', 'Belum Dipakai']
    voucher_data = [voucher_used, voucher_unused]
    
    # Voucher berdasarkan nilai diskon (Dinamis sesuai data)
    voucher_type_labels = []
    voucher_type_data = []
    
    unique_values = coupons_filtered.values_list('discount_value', flat=True).distinct()
    for val in sorted(unique_values):
        count = coupons_filtered.filter(discount_value=val).count()
        voucher_type_labels.append(f'Voucher Rp {val:,}'.replace(',', '.'))
        voucher_type_data.append(count)
    
    if not voucher_type_labels:
        voucher_type_labels = ['Belum ada data']
        voucher_type_data = [0]
    
    # Total nilai diskon yang sudah diberikan
    total_discount_given = coupons_filtered.filter(is_used=True).aggregate(Sum('discount_value'))['discount_value__sum'] or 0
    
    # --- DATA RATING DISTRIBUTION (TERFILTER) ---
    rating_labels = ['⭐ 1', '⭐⭐ 2', '⭐⭐⭐ 3', '⭐⭐⭐⭐ 4', '⭐⭐⭐⭐⭐ 5']
    rating_data = []
    for i in range(1, 6):
        count = reviews_filtered.filter(rating=i).count()
        rating_data.append(count)
    
    # Average rating
    avg_rating = reviews_filtered.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    total_reviews = reviews_filtered.count()
    
    # --- DATA USER INTEREST (TERFILTER) ---
    interest_data = interests_filtered.values('brand__brand_name', 'category__category_name').annotate(
        total_score=Sum('score')
    ).order_by('-total_score')[:5]
    interest_labels = []
    interest_scores = []
    for item in interest_data:
        name = item['brand__brand_name'] or item['category__category_name'] or 'Unknown'
        interest_labels.append(name)
        interest_scores.append(item['total_score'] or 0)
    
    if not interest_labels:
        interest_labels = ['Belum ada data']
        interest_scores = [0]
    
    return {
        'total_revenue': revenue,
        'unpaid_orders': unpaid_orders,
        'to_ship': to_ship,
        'shipping': shipping,
        'completed': completed,
        'cancelled': cancelled,
        'total_orders': total_orders,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'period': period,
        'start_custom': start_custom,
        'end_custom': end_custom,
        'retur_pending': retur_pending,
        'retur_proses': retur_proses,
        'retur_selesai': retur_selesai,
        'retur_ditolak': retur_ditolak,
        'chart_labels': chart_labels,
        'chart_order_data': chart_order_data,
        'chart_revenue_data': chart_revenue_data,
        'payment_labels': ['Belum ada data'],
        'payment_data': [0],
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        'brand_labels': brand_labels,
        'brand_data': brand_data,
        'category_labels': category_labels,
        'category_data': category_data,
        'user_chart_labels': user_chart_labels,
        'user_chart_data': user_chart_data,
        'voucher_labels': voucher_labels,
        'voucher_data': voucher_data,
        'voucher_type_labels': voucher_type_labels,
        'voucher_type_data': voucher_type_data,
        'total_discount_given': total_discount_given,
        'rating_labels': rating_labels,
        'rating_data': rating_data,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'interest_labels': interest_labels,
        'interest_scores': interest_scores,
    }

# --- 3. PROSES OVERRIDE INDEX ADMIN ---
original_index = admin.site.index 

def custom_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    
    period = request.GET.get('period')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    extra_context.update(get_dashboard_data(period, start_date, end_date))
    return original_index(request, extra_context)

admin.site.index = custom_index
admin.site.index_template = 'admin/index.html'

# --- 4. KONFIGURASI MODEL ADMIN ---
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'order_total', 'grand_total', 'status_display', 'aksi_tombol', 'created_at']
    list_filter = ['status', TrackingFilter]
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email', 'tracking_number')
    list_per_page = 20
    readonly_fields = ('order_number', 'snap_token', 'created_at', 'order_total', 'grand_total', 'discount')
    inlines = [OrderProductInline]
    
    fieldsets = (
        ('Informasi Transaksi', {
            'fields': ('order_number', 'snap_token', 'status', 'is_ordered', 'created_at')
        }),
        ('Informasi Pelanggan', {
            'fields': ('user', 'first_name', 'last_name', 'phone', 'email')
        }),
        ('Alamat Pengiriman', {
            'fields': ('address', 'province', 'city', 'district', 'postal_code')
        }),
        ('Rincian Biaya', {
            'fields': ('order_total', 'shipping_service', 'shipping_cost', 'discount', 'grand_total')
        }),
        ('Catatan & Pelacakan', {
            'fields': ('order_note', 'tracking_number')
        }),
    )

    def status_display(self, obj):
        if obj.status == 'New':
            return format_html('<span style="color: #ffc107; font-weight: bold;">⏳ Menunggu Pembayaran</span>')
        elif obj.status == 'Pending':
            return format_html('<span style="color: #17a2b8; font-weight: bold;">💳 Pembayaran Berhasil</span>')
        elif obj.status == 'Accepted':
            if obj.tracking_number:
                return format_html('<span style="color: #fd7e14; font-weight: bold;">🚚 Sedang Dikirim</span>')
            return format_html('<span style="color: #007bff; font-weight: bold;">📦 Sedang Diproses</span>')
        elif obj.status == 'Completed':
            return format_html('<span style="color: #28a745; font-weight: bold;">✅ Selesai</span>')
        elif obj.status == 'Cancelled':
            return format_html('<span style="color: #dc3545; font-weight: bold;">❌ Dibatalkan</span>')
        return obj.status

    status_display.short_description = 'Status Pesanan'
    
    def aksi_tombol(self, obj):
        pdf_url = reverse('admin_order_pdf', args=[obj.id])
        edit_url = reverse('admin:order_order_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 5px;">Detail</a>'
            '<a class="button" href="{}" target="_blank" style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Cetak PDF</a>',
            edit_url, pdf_url
        )
    aksi_tombol.short_description = 'Aksi'

admin.site.register(Order, OrderAdmin)

admin.site.register(OrderProduct)


#RETUR PRODUK
@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'bank_name', 'created_at', 'aksi_tombol']
    list_filter = ['status', 'created_at']
    readonly_fields = ['order', 'reason', 'image_proof', 'bank_name', 'bank_account_number', 'bank_account_name', 'created_at']
    
    # Supaya Admin bisa kasih catatan dan update status saja
    fields = ['order', 'status', 'admin_note', 'reason', 'image_proof', 'refund_proof', 'bank_name', 'bank_account_number', 'bank_account_name']

    # Fungsi opsional: Agar foto bukti bisa langsung intip di admin
    def view_proof(self, obj):
        return format_html('<img src="{}" width="150" />'.format(obj.image_proof.url))

    def aksi_tombol(self, obj):
        edit_url = reverse('admin:order_returnrequest_change', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Kelola</a>', edit_url)
    aksi_tombol.short_description = 'Aksi'
    
    
#Voucher
# Cara sederhana untuk menampilkan tabel Kupon
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # Kolom apa saja yang mau ditampilkan di daftar tabel
    list_display = ('code', 'user', 'discount_value', 'is_used', 'created_at', 'aksi_tombol')
    
    # Fitur filter di samping kanan
    list_filter = ('is_used', 'created_at')
    
    # Fitur pencarian berdasarkan kode atau email user
    search_fields = ('code', 'user__email')

    def aksi_tombol(self, obj):
        edit_url = reverse('admin:order_coupon_change', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Ubah</a>', edit_url)
    aksi_tombol.short_description = 'Aksi'

    
    
