from django.db import models
from account.models import Account
from store.models import Product

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'), 
        ('Accepted', 'Accepted'), 
        ('Completed', 'Completed'), 
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    
    # 1. Info Kontak
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    
    # 2. Info Alamat & RajaOngkir
    address = models.CharField(max_length=200)
    
    province_id = models.CharField(max_length=10, blank=True)
    province = models.CharField(max_length=50)
    city_id = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=50)
    
    # === INI YANG HILANG SEBELUMNYA (KECAMATAN & KELURAHAN) ===
    district_id = models.CharField(max_length=10, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    subdistrict_id = models.CharField(max_length=10, blank=True, null=True)
    subdistrict = models.CharField(max_length=50, blank=True, null=True)
    # ==========================================================
    
    postal_code = models.CharField(max_length=10)
    
    # 3. Info Finansial
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField() 
    shipping_cost = models.FloatField() 
    grand_total = models.FloatField() 
    
    # 4. Status Tracking
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    tracking_number = models.CharField(max_length=50, blank=True) 
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    snap_token = models.CharField(max_length=100, blank=True, null=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return self.address

    def __str__(self):
        return self.first_name
    
    def save(self, *args, **kwargs):
        # Jika pesanan ini sudah ada di database (bukan pesanan baru)
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            # Jika status berubah dari apapun MENJADI 'Cancelled'
            if old_order.status != 'Cancelled' and self.status == 'Cancelled':
                # Ambil semua produk di dalam pesanan ini
                order_products = OrderProduct.objects.filter(order=self)
                for item in order_products:
                    product = item.product
                    product.stock += item.quantity # Kembalikan stok
                    product.save()
                    
        super(Order, self).save(*args, **kwargs)


class OrderProduct(models.Model):
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