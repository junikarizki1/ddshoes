from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from .models import Product

@receiver(post_save, sender=Product)
def send_new_product_notification(sender, instance, created, **kwargs):
    if created:
        from order.models import OrderProduct

        # Cari semua OrderProduct yang berasal dari Order berstatus Completed
        # Dan produknya memiliki Kategori ATAU Brand yang sama dengan produk baru
        if instance.brand:
            qs = OrderProduct.objects.filter(
                order__status='Completed'
            ).filter(
                Q(product__category=instance.category) | Q(product__brand=instance.brand)
            ).select_related('order')
        else:
            qs = OrderProduct.objects.filter(
                order__status='Completed',
                product__category=instance.category
            ).select_related('order')

        # Dapatkan daftar email unik beserta nama depan
        users_to_email = {}
        for op in qs:
            email = op.order.email
            if email and email not in users_to_email:
                users_to_email[email] = op.order.first_name

        # Kirim email ke setiap user
        for email, first_name in users_to_email.items():
            mail_subject = f'Produk Baru Sesuai Selera Anda: {instance.product_name}!'
            context = {
                'first_name': first_name,
                'product': instance,
            }
            
            message_html = render_to_string('store/new_product_email.html', context)
            
            send_email = EmailMultiAlternatives(
                subject=mail_subject,
                body=f"Halo {first_name}, kami memiliki koleksi terbaru yang mungkin Anda sukai: {instance.product_name}.",
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            send_email.attach_alternative(message_html, "text/html")
            
            try:
                send_email.send()
                print(f"DEBUG: Email notifikasi produk baru '{instance.product_name}' terkirim ke {email}")
            except Exception as e:
                print(f"Gagal mengirim email ke {email}: {e}")