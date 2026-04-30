from django.db import models
from django.urls import reverse
from account.models import Account

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

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'

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

