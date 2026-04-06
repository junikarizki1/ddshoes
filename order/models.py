from django.db import models
from account.models import Account
from store.models import Product

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'), # Untuk menunggu pembayaran Midtrans
        ('Accepted', 'Accepted'), # Pembayaran berhasil
        ('Completed', 'Completed'), # Barang sudah sampai
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    
    # 1. Info Kontak (Sesuai Standar Midtrans)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    
    # 2. Info Alamat & RajaOngkir (Disederhanakan menjadi 1 baris)
    address = models.CharField(max_length=200)
    
    # Kita simpan ID-nya untuk API RajaOngkir, dan Nama-nya untuk ditampilkan di web agar tidak perlu request API terus-menerus
    province_id = models.CharField(max_length=10, blank=True)
    province = models.CharField(max_length=50)
    city_id = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    
    # 3. Info Finansial
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField() # Total harga sepatu
    shipping_cost = models.FloatField() # Ongkos kirim dari RajaOngkir
    grand_total = models.FloatField() # Total keseluruhan yang ditagihkan Midtrans
    
    # 4. Status Tracking
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    tracking_number = models.CharField(max_length=50, blank=True) # Resi JNE/J&T
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return self.address

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    # Tabel ini menyimpan rincian SEPATU APA SAJA yang ada di dalam satu nomor pesanan
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name