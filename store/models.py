from django.db import models
from django.urls import reverse
from account.models import Account
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# 1. MODEL KATEGORI (Untuk Sidebar "Browse Categories")
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name

class Brand(models.Model):
    brand_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    brand_image = models.ImageField(upload_to='photos/brands', blank=True)

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        
    def get_url(self):
        return reverse('products_by_brand', args=[self.slug])

    def __str__(self):
        return self.brand_name

# 2. MODEL PRODUK (Data Utama Sepatu)
class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    
    # Relasi ke Kategori
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand           = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    size = models.IntegerField(default=0)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        # Baris ini akan memaksa slug dibuat ulang setiap kali nama produk diubah/disimpan
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

# 5. MODEL GALLERY (Opsional: Jika 1 produk punya banyak foto kecil-kecil)
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


#Model Untuk Menangkap kebiasaan user agar bisa dipersonalisasi
class UserInterest(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    last_action = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.brand or self.category} ({self.score})"


#Model Rating atau review
class ReviewRating(models.Model):
    # Perbaikan E301: Menggunakan settings.AUTH_USER_MODEL agar relasi User aman
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Perbaikan E300 & E307: Hubungkan ke app 'orders' tempat model 'Order' berada
    # JIKA nama aplikasi order Anda bukan 'orders', ganti teks 'orders.Order' di bawah ini
    order = models.OneToOneField('order.Order', on_delete=models.CASCADE, related_name='review')
    
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_anonymous = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def masked_username(self):
        username = self.user.username
        if len(username) <= 2:
            # Jika username sangat pendek (misal: "Ab"), tampilkan huruf pertama ditambah bintang
            return username[0] + "*"
        else:
            # Ambil huruf pertama + bintang-bintang + huruf terakhir (Misal: "Randi" -> "R***i")
            return f"{username[0]}***{username[-1]}"

    def __str__(self):
        return f"Review {self.user.username} - Order #{self.order.order_number}"


# =========================================================
# SIGNAL: Broadcast email ke pelanggan saat produk baru diupload
# Hanya kirim ke user yang pernah beli brand/kategori yang sama
# =========================================================
@receiver(post_save, sender=Product)
def broadcast_new_product_email(sender, instance, created, **kwargs):
    if not created:
        return  # Hanya untuk produk baru, bukan edit

    try:
        from order.models import OrderProduct

        # Cari user yang pernah beli produk dengan brand ATAU category yang sama
        matched_user_ids = OrderProduct.objects.filter(
            order__is_ordered=True
        ).filter(
            models.Q(product__brand=instance.brand) |
            models.Q(product__category=instance.category)
        ).values_list('user_id', flat=True).distinct()

        if not matched_user_ids:
            return

        recipients = Account.objects.filter(
            id__in=matched_user_ids,
            is_active=True
        ).exclude(email='')

        for user in recipients:
            try:
                subject = f'Koleksi Baru untuk Kamu — {instance.product_name}'
                message = render_to_string('store/new_product_email.html', {
                    'first_name': user.first_name or user.username,
                    'product': instance,
                    'product_url': f"https://{settings.ALLOWED_HOSTS[0]}{instance.get_url()}",
                })
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                email.content_subtype = 'html'
                email.send()
                print(f"Broadcast terkirim ke {user.email}")
            except Exception as e:
                print(f"Gagal kirim ke {user.email}: {e}")

    except Exception as e:
        print(f"Error broadcast signal: {e}")
