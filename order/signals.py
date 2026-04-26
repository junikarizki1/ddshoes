import string
import random
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order, Coupon

@receiver(pre_save, sender=Order)
def capture_old_status(sender, instance, **kwargs):
    """
    Mengambil status pesanan lama sebelum disimpan untuk mendeteksi perubahan.
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Order)
def handle_loyalty_logic(sender, instance, created, **kwargs):
    customer = instance.user
    amount = Decimal(str(instance.order_total))
    
    # 1. LOGIKA TAMBAH (Jika status adalah Completed)
    if instance.status == 'Completed':
        # Cek apakah transaksi ini sudah pernah diproses (mencegah double point)
        # Kita bisa asumsikan jika saldo bertambah, proses kelipatan berjalan
        customer.loyalty_balance += amount
        customer.save()

        while customer.loyalty_balance >= Decimal('200000'):
            customer.loyalty_balance -= Decimal('200000')
            customer.save()
            
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            voucher_code = f"LOYAL-{random_str}"
            
            Coupon.objects.create(
                user=customer,
                code=voucher_code,
                discount_value=5000
            )
            # ... (Kirim email jika perlu)

    # 2. LOGIKA SAPUJAGAT (Jika status BUKAN Completed)
    # Ini akan mengeksekusi penghapusan jika status diubah ke Refunded, Cancelled, dll.
    else:
        # Cek apakah user punya voucher 'LOYAL-' yang belum terpakai
        # Dan apakah saldo user mencurigakan (atau kita tarik paksa saldo sejumlah amount)
        customer.loyalty_balance -= amount
        
        # Tarik kembali voucher selama saldo di bawah 0
        while customer.loyalty_balance < 0:
            voucher_batal = Coupon.objects.filter(
                user=customer, 
                is_used=False, 
                code__startswith="LOYAL-"
            ).last()

            if voucher_batal:
                voucher_batal.delete()
                customer.loyalty_balance += Decimal('200000')
                print(f"DEBUG: Voucher {voucher_batal.code} BERHASIL DIHAPUS")
            else:
                customer.loyalty_balance = Decimal('0.00')
                break
        
        customer.save()