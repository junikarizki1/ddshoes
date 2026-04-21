from django.contrib import admin
from .models import Order, OrderProduct

# Ini agar Anda bisa melihat rincian sepatu apa saja yang dibeli di dalam 1 pesanan
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    # Kolom yang akan tampil di tabel halaman depan Admin
    list_display = ['order_number', 'full_name', 'phone', 'city', 'order_total', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]
    
    # Kolom yang bisa diedit langsung tanpa perlu masuk ke detail
    list_editable = ['status', 'is_ordered']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)