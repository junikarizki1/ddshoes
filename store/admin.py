from django.contrib import admin
from .models import Product, Category, ProductGallery, Brand, UserInterest, Account, ReviewRating
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'brand', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('brand_name',)}
    list_display = ('brand_name', 'slug')
    
class ReviewRatingAdmin(admin.ModelAdmin):
    # list_display menentukan kolom apa saja yang muncul di tabel utama admin
    # Kita panggil 'masked_username' sebagai kolom penunjuk nama samaran
    list_display = ['order', 'user', 'masked_username', 'rating', 'is_anonymous', 'is_visible', 'created_at']
    
    # list_editable membuat admin bisa langsung mencentang/mematikan visibilitas ulasan tanpa klik buka detail data
    list_editable = ['is_visible'] 
    
    # list_filter menambahkan kotak filter di sebelah kanan untuk menyaring ulasan berdasarkan kriteria tertentu
    list_filter = ['rating', 'is_visible', 'is_anonymous', 'created_at']
    
    # search_fields menyediakan kolom pencarian berdasarkan username atau nomor pesanan
    search_fields = ['user__username', 'order__order_number', 'subject', 'review']

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'category', 'score', 'last_action')
    list_filter = ('brand', 'category')
    search_fields = ('user__email', 'brand__brand_name', 'category__category_name')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductGallery)
admin.site.register(ReviewRating, ReviewRatingAdmin)