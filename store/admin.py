from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Product, Category, ProductGallery, Brand, UserInterest, ReviewRating
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'product_name', 'price', 'stock', 'category', 'brand', 'modified_date', 'is_available', 'aksi_link')
    list_display_links = ('thumbnail_preview', 'product_name')
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('category', 'brand', 'is_available')
    search_fields = ('product_name', 'description')
    list_editable = ('price', 'stock', 'is_available')
    list_per_page = 20
    inlines = [ProductGalleryInline]
    
    def thumbnail_preview(self, obj):
        if obj.images:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.images.url)
        return format_html('<span style="color: #999;">No Image</span>')
    thumbnail_preview.short_description = 'Foto'

    def aksi_link(self, obj):
        edit_url = reverse('admin:store_product_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 5px;">Edit</a>'
            '<a class="button" href="{}" target="_blank" style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Lihat Toko</a>',
            edit_url, obj.get_url()
        )
    aksi_link.short_description = 'Aksi'

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('cat_thumbnail', 'category_name', 'slug', 'aksi_link')
    list_display_links = ('cat_thumbnail', 'category_name')
    search_fields = ('category_name',)
    list_per_page = 20
    
    def cat_thumbnail(self, obj):
        if obj.cat_image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.cat_image.url)
        return format_html('<span style="color: #999;">No Image</span>')
    cat_thumbnail.short_description = 'Ikon'

    def aksi_link(self, obj):
        edit_url = reverse('admin:store_category_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 5px;">Edit</a>'
            '<a class="button" href="{}" target="_blank" style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Lihat Toko</a>',
            edit_url, obj.get_url()
        )
    aksi_link.short_description = 'Aksi'

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('brand_name',)}
    list_display = ('brand_thumbnail', 'brand_name', 'slug', 'aksi_link')
    list_display_links = ('brand_thumbnail', 'brand_name')
    search_fields = ('brand_name',)
    list_per_page = 20
    
    def brand_thumbnail(self, obj):
        if obj.brand_image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.brand_image.url)
        return format_html('<span style="color: #999;">No Image</span>')
    brand_thumbnail.short_description = 'Logo'

    def aksi_link(self, obj):
        edit_url = reverse('admin:store_brand_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 5px;">Edit</a>'
            '<a class="button" href="{}" target="_blank" style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Lihat Toko</a>',
            edit_url, obj.get_url()
        )
    aksi_link.short_description = 'Aksi'

    
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'masked_username', 'rating', 'is_anonymous', 'is_visible', 'created_at']
    list_editable = ['is_visible'] 
    list_filter = ['rating', 'is_visible', 'is_anonymous', 'created_at']
    search_fields = ['user__username', 'order__order_number', 'subject', 'review']
    list_per_page = 20

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'category', 'score', 'last_action')
    list_filter = ('brand', 'category')
    search_fields = ('user__email', 'brand__brand_name', 'category__category_name')
    list_per_page = 20

@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'gallery_thumbnail')
    search_fields = ('product__product_name',)
    list_per_page = 20
    
    def gallery_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; border-radius: 4px;" />', obj.image.url)
        return format_html('<span style="color: #999;">No Image</span>')
    gallery_thumbnail.short_description = 'Gambar'

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)