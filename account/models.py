from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 1. Class Manager: Mengatur cara membuat User biasa dan Superadmin
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User harus memiliki alamat email')
        if not username:
            raise ValueError('User harus memiliki username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        # Wajib set True agar bisa masuk Django Admin jika menggunakan PermissionsMixin
        user.is_superuser = True 
        user.save(using=self._db)
        return user

# 2. Class Account: Struktur tabel User di Database
# Tambahkan PermissionsMixin di dalam kurung setelah AbstractBaseUser
class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    loyalty_balance = models.FloatField(default=0)
    shoe_size = models.IntegerField(null=True, blank=True)

    # Field wajib Django
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True) # Gunakan auto_now agar update tiap login
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) 
    is_superadmin = models.BooleanField(default=False)

    # MENJADIKAN EMAIL SEBAGAI LOGIN UTAMA
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    # Jika pakai PermissionsMixin, fungsi has_perm dan has_module_perms 
    # di bawah ini opsional, tapi boleh tetap ada untuk custom logic.
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


# Model Alamat Terpisah (Multi-Address Support)
class Address(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Alamat Baru')
    province_id = models.CharField(max_length=20)
    province_name = models.CharField(max_length=100)
    city_id = models.CharField(max_length=20)
    city_name = models.CharField(max_length=100)
    district_id = models.CharField(max_length=20)
    district_name = models.CharField(max_length=100)
    subdistrict_id = models.CharField(max_length=20)
    subdistrict_name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    address = models.TextField()
    shipping_service = models.CharField(max_length=100, blank=True)
    shipping_cost = models.FloatField(default=0)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.label} - {self.user.email}"