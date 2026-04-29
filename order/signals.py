import string
import random
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order, Coupon

@receiver(pre_save, sender=Order)
def capture_old_status(sender, instance, **kwargs):

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
    # Gunakan float karena loyalty_balance di model Account adalah FloatField
    amount = float(instance.order_total)
    old_status = getattr(instance, '_old_status', None)

    # 1. LOGIKA TAMBAH (Hanya jika status BERUBAH menjadi Completed)
    if instance.status == 'Completed' and old_status != 'Completed':
        customer.loyalty_balance += amount
        
        # Kelipatan 200rb
        while customer.loyalty_balance >= 200000:
            customer.loyalty_balance -= 200000
            
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            voucher_code = f"LOYAL-{random_str}"
            
            Coupon.objects.create(
                user=customer,
                code=voucher_code,
                discount_value=5000,
                is_used=False
            )
        customer.save()

    # 2. LOGIKA BATAL (Hanya jika status berubah DARI Completed MENJADI Cancelled/Refunded)
    elif old_status == 'Completed' and instance.status in ['Cancelled', 'Refunded']:
        customer.loyalty_balance -= amount
        
        # Jika saldo minus, tarik kembali voucher yang belum terpakai
        while customer.loyalty_balance < 0:
            voucher_batal = Coupon.objects.filter(
                user=customer, 
                is_used=False, 
                code__startswith="LOYAL-"
            ).last()

            if voucher_batal:
                voucher_batal.delete()
                customer.loyalty_balance += 200000
            else:
                # Jika tidak ada voucher untuk ditarik, mentok di angka 0
                customer.loyalty_balance = 0.0
                break
        
        customer.save()