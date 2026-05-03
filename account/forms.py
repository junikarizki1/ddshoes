from django import forms
from .models import Account
from django.contrib.auth import password_validation

class RegistrationForm(forms.ModelForm):
    # Definisi field password manual untuk mendukung widget PasswordInput
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
        }),
        label="Password"
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ulangi Password',
        }),
        label="Konfirmasi Password"
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'shoe_size']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        
        # 1. GENERATE KETENTUAN PASSWORD (HELP TEXT)
        # Mengambil aturan dari AUTH_PASSWORD_VALIDATORS di settings.py
        validators = password_validation.get_default_password_validators()
        help_texts = [v.get_help_text() for v in validators]
        self.fields['password'].help_text = '<ul class="helptext"><li>' + '</li><li>'.join(help_texts) + '</li></ul>'
        
        # 2. TAMBAHKAN CLASS BOOTSTRAP KE SEMUA FIELD
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        """
        Melakukan validasi menyeluruh terhadap data yang diinput
        """
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # VALIDASI 1: Cek apakah password dan ulangi password cocok
        if password and confirm_password:
            if password != confirm_password:
                # Menambahkan error spesifik pada field confirm_password
                self.add_error('confirm_password', "Password tidak cocok! Silakan periksa kembali.")
        
        # VALIDASI 2: Paksa pengecekan aturan keamanan Django (Min 8 karakter, bukan angka saja, dll)
        if password:
            try:
                # Ini akan memicu error jika password seperti "haha12" dimasukkan
                password_validation.validate_password(password)
            except forms.ValidationError as e:
                # Menambahkan error keamanan ke field password
                self.add_error('password', e)

        return cleaned_data