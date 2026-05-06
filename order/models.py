from django.db import models
from account.models import Account
from store.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class Order(models.Model):
    snap_token = models.CharField(max_length=100, blank=True, null=True)
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'), 
        ('Accepted', 'Accepted'), 
        ('Completed', 'Completed'), 
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10)
    order_total = models.FloatField() 
    shipping_cost = models.FloatField() 
    grand_total = models.FloatField() 
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    tracking_number = models.CharField(max_length=50, blank=True) 
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    snap_token = models.CharField(max_length=255, blank=True, null=True)
    discount = models.FloatField(default=0)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f"{self.order_number} - {self.first_name}"

    def save(self, *args, **kwargs):
        # Logika Balikin Stok untuk Pembatalan Manual (Bukan Retur)
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            # Jika admin mengubah status ke Cancelled secara manual
            if old_order.status != 'Cancelled' and self.status == 'Cancelled':
                for item in self.orderproduct_set.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()
        super(Order, self).save(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.product_name


class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Menunggu Persetujuan'),
        ('Approved', 'Disetujui (Silakan Kirim Barang)'),
        ('Refunded', 'Dana Telah Dikembalikan'),
        ('Rejected', 'Permintaan Ditolak'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='return_request')
    reason = models.TextField()
    image_proof = models.ImageField(upload_to='photos/returns/')
    bank_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=50)
    bank_account_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_note = models.TextField(blank=True, null=True)
    refund_proof = models.ImageField(upload_to='photos/refund_proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Retur untuk Order #{self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # 1. Jalankan save bawaan dulu agar data ReturnRequest tersimpan
        super(ReturnRequest, self).save(*args, **kwargs)
        
        # 2. Cek jika statusnya Refunded, paksa update ke tabel Order
        if self.status == 'Refunded':
            # Gunakan filter().update() karena ini metode paling 'galak' di Django
            Order.objects.filter(pk=self.order.pk).update(status='Returned')
            
            # 3. Logika kembalikan stok
            order_items = self.order.orderproduct_set.all()
            for item in order_items:
                product = item.product
                product.stock += item.quantity
                product.save()
            
            print(f"DEBUG: Status Order #{self.order.order_number} BERHASIL dipaksa menjadi Returned")
# Signal Notifikasi Pengiriman
@receiver(post_save, sender=Order)
def send_shipping_notification(sender, instance, created, **kwargs):
    if not created and instance.tracking_number:
        # Gunakan atribut sementara untuk mencegah email ganda dalam satu sesi save
        if not hasattr(instance, '_email_already_sent'):
            try:
                mail_subject = f'Pesanan #{instance.order_number} Sedang Dalam Perjalanan!'
                message = render_to_string('order/shipping_email.html', {'order': instance})
                send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, [instance.email])
                send_email.content_subtype = "html"
                send_email.send()
                instance._email_already_sent = True
            except Exception as e:
                print(f"Gagal mengirim email: {e}")
                
#Model Voucher
class Coupon(models.Model):
    user = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    discount_value = models.IntegerField(default=5000) # Potongan 5rb
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.code} - {self.user.email}"
    
