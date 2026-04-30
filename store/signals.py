from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserInterest, Product

# Fungsi ini akan dipanggil nanti di views detail produk
def update_user_interest(user, product, action_weight):
    # Update skor untuk Brand
    brand_interest, created = UserInterest.objects.get_or_create(
        user=user, brand=product.brand
    )
    brand_interest.score += action_weight
    brand_interest.save()

    # Update skor untuk Kategori
    cat_interest, created = UserInterest.objects.get_or_create(
        user=user, category=product.category
    )
    cat_interest.score += action_weight
    cat_interest.save()