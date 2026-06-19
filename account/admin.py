from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import Account, Address

class AccountAdmin(UserAdmin):
    list_display = ('photo_preview', 'email', 'first_name', 'last_name', 'username', 'shoe_size', 'loyalty_balance', 'is_active', 'is_staff', 'aksi_link')
    list_display_links = ('photo_preview', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    list_per_page = 20
    
    filter_horizontal = ()
    list_filter = ('is_active', 'is_staff', 'is_superadmin')
    
    fieldsets = (
        ('Kredensial & Otorisasi', {
            'fields': ('email', 'username', 'password')
        }),
        ('Informasi Profil', {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_photo', 'shoe_size')
        }),
        ('Loyalitas & Saldo', {
            'fields': ('loyalty_balance',)
        }),
        ('Hak Akses', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'is_superadmin', 'is_superuser')
        }),
        ('Log Riwayat', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    def photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.profile_photo.url)
        return format_html('<span style="color: #999;">No Photo</span>')
    photo_preview.short_description = 'Foto'

    def aksi_link(self, obj):
        edit_url = reverse('admin:account_account_change', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Edit</a>', edit_url)
    aksi_link.short_description = 'Aksi'

class AddressAdmin(admin.ModelAdmin):
    list_display = ('label', 'user', 'province_name', 'city_name', 'district_name', 'postal_code', 'is_default', 'aksi_link')
    list_filter = ('province_name', 'is_default')
    search_fields = ('user__email', 'label', 'address')
    list_per_page = 20

    def aksi_link(self, obj):
        edit_url = reverse('admin:account_address_change', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Edit</a>', edit_url)
    aksi_link.short_description = 'Aksi'

admin.site.register(Account, AccountAdmin)
admin.site.register(Address, AddressAdmin)
