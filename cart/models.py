from django.db import models
from store.models import Product
from account.models import Account # Wajib import model Account

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    # PERUBAHAN: Tambahkan Field User ini
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Cart (session) kita buat null=True karena kita sekarang pakai user
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True) 
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name