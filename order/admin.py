from django.contrib import admin
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderProduct, Coupon, Account
from store.models import Product
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
def get_dashboard_data(period=None, start_custom=None, end_custom=None):
    orders = Order.objects.all()
    returns = ReturnRequest.objects.all()
    now = timezone.now()

    # Logika Filter Tanggal (Bebas / Shortcut)
    if start_custom and end_custom:
        orders = orders.filter(created_at__date__range=[start_custom, end_custom])
    elif period == 'today':
        orders = orders.filter(created_at__date=now.date())
    elif period == 'week':
        orders = orders.filter(created_at__gte=now - timedelta(days=7))
    elif period == 'month':
        orders = orders.filter(created_at__year=now.year, created_at__month=now.month)
    
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
# Stok Habis: Benar-benar nol
    out_of_stock = Product.objects.filter(stock=0).count()
    
    # Stok Menipis: Hanya jika sisa tepat 1 (Sesuai request kamu)
    low_stock = Product.objects.filter(stock=1).count()
    
    # --- HITUNG STATISTIK RETUR (BARU) ---
    retur_pending = returns.filter(status='Pending').count()
    retur_proses  = returns.filter(status='Approved').count()
    retur_selesai = returns.filter(status='Refunded').count()
    retur_ditolak = returns.filter(status='Rejected').count()
    
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
    # Ganti 'status' menjadi 'status_display' di list_display
    list_display = ['order_number', 'full_name','order_total', 'grand_total', 'status_display', 'cetak_invoice', 'created_at']
    list_filter = [
        'status',TrackingFilter       
    ]

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
    
#INVOICE PDF    
    def cetak_invoice(self, obj):
        # Membuat tombol hijau kecil di tabel admin
        url = reverse('admin_order_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">Cetak PDF</a>', url)
    
    cetak_invoice.short_description = 'Invoice'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)


#RETUR PRODUK
@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'bank_name', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['order', 'reason', 'image_proof', 'bank_name', 'bank_account_number', 'bank_account_name', 'created_at']
    
    # Supaya Admin bisa kasih catatan dan update status saja
    fields = ['order', 'status', 'admin_note', 'reason', 'image_proof', 'refund_proof', 'bank_name', 'bank_account_number', 'bank_account_name']

    # Fungsi opsional: Agar foto bukti bisa langsung intip di admin
    def view_proof(self, obj):
        from django.utils.html import format_html
        return format_html('<img src="{}" width="150" />'.format(obj.image_proof.url))
    
    
#Voucher
# Cara sederhana untuk menampilkan tabel Kupon
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # Kolom apa saja yang mau ditampilkan di daftar tabel
    list_display = ('code', 'user', 'discount_value', 'is_used', 'created_at')
    
    # Fitur filter di samping kanan
    list_filter = ('is_used', 'created_at')
    
    # Fitur pencarian berdasarkan kode atau email user
    search_fields = ('code', 'user__email')
    
    
